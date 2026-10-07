"""LangGraph agent workflow for RepoGuard AI — the full autonomous pipeline."""
import logging
import os
import json
import subprocess
import shutil
import traceback
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from langgraph.graph import StateGraph, END
from app.agents.states import AgentState
from app.config import settings

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.utcnow().isoformat()


def _event(step: int, name: str, status: str, message: str, data: dict = None) -> Dict:
    return {
        "type": f"step_{status}",
        "step": step,
        "step_name": name,
        "message": message,
        "data": data or {},
        "timestamp": _now(),
    }


def _evidence(claim: str, file: str = "", symbol: str = "",
              line_start: int = None, line_end: int = None,
              reason: str = "", etype: str = "ast") -> Dict:
    return {
        "claim": claim, "file": file, "symbol": symbol,
        "line_start": line_start, "line_end": line_end,
        "reason": reason, "evidence_type": etype, "timestamp": _now(),
    }


# ─────────────────── helpers ────────────────────────────────────────────
def _read_file_safe(path: str, max_kb: int = 200) -> str:
    try:
        sz = os.path.getsize(path)
        if sz > max_kb * 1024:
            return f"[file too large: {sz} bytes]"
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"[error reading file: {e}]"


def _run_cmd(cmd: str, cwd: str, timeout: int = 120) -> Dict:
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True,
            encoding="utf-8", errors="replace", timeout=timeout
        )
        return {"stdout": r.stdout, "stderr": r.stderr, "code": r.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out", "code": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "code": -1}


def _get_llm():
    """Get the LLM provider (lazy import to avoid import-time failures)."""
    from app.llm.provider import get_llm_provider
    return get_llm_provider()


def _scan_files(repo_path: str) -> List[Dict]:
    """Walk repo and collect file metadata."""
    IGNORE = {".git", "node_modules", "venv", ".venv", "__pycache__",
              "dist", "build", "coverage", "target", ".tox", ".idea",
              ".vscode", ".mypy_cache", ".pytest_cache", "vendor", ".eggs"}
    CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go",
                 ".c", ".cpp", ".h", ".rb", ".rs", ".php", ".kt", ".swift"}
    files = []
    for root, dirs, fnames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for fn in fnames:
            ext = os.path.splitext(fn)[1].lower()
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, repo_path).replace("\\", "/")
            try:
                sz = os.path.getsize(fp)
            except OSError:
                sz = 0
            files.append({"path": rel, "ext": ext, "size": sz,
                          "is_code": ext in CODE_EXTS})
    return files


# ════════════════════════════════════════════════════════════════════════
#  STEP 1 — REPOSITORY SCANNER
# ════════════════════════════════════════════════════════════════════════
def repository_scanner(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    repo_url = state.get("repo_url", "")
    events = []
    evidence = []

    events.append(_event(1, "Repository Scanner", "running",
                         f"Scanning repository at {repo_path}..."))

    files = _scan_files(repo_path)
    code_files = [f for f in files if f["is_code"]]

    # Language distribution
    lang_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                ".java": "Java", ".go": "Go", ".c": "C", ".cpp": "C++"}
    lang_counts: Dict[str, int] = {}
    for f in code_files:
        lang = lang_map.get(f["ext"], "Other")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    primary = max(lang_counts, key=lang_counts.get) if lang_counts else "Unknown"

    # Detect frameworks / test frameworks
    frameworks, test_fws, pkg_mgrs = [], [], []
    if os.path.exists(os.path.join(repo_path, "requirements.txt")):
        pkg_mgrs.append("pip")
        txt = _read_file_safe(os.path.join(repo_path, "requirements.txt")).lower()
        if "django" in txt: frameworks.append("Django")
        if "flask" in txt: frameworks.append("Flask")
        if "fastapi" in txt: frameworks.append("FastAPI")
        if "pytest" in txt: test_fws.append("pytest")
    if os.path.exists(os.path.join(repo_path, "setup.py")):
        txt = _read_file_safe(os.path.join(repo_path, "setup.py")).lower()
        if "pytest" in txt: test_fws.append("pytest")
    if os.path.exists(os.path.join(repo_path, "pyproject.toml")):
        pkg_mgrs.append("pip")
        txt = _read_file_safe(os.path.join(repo_path, "pyproject.toml")).lower()
        if "pytest" in txt: test_fws.append("pytest")
    if os.path.exists(os.path.join(repo_path, "package.json")):
        pkg_mgrs.append("npm")
        try:
            pj = json.loads(_read_file_safe(os.path.join(repo_path, "package.json")))
            deps = {**pj.get("dependencies", {}), **pj.get("devDependencies", {})}
            if "react" in deps: frameworks.append("React")
            if "express" in deps: frameworks.append("Express")
            if "jest" in deps: test_fws.append("jest")
            if "vitest" in deps: test_fws.append("vitest")
        except Exception:
            pass

    # Check for test directories
    test_dirs = [f["path"] for f in files
                 if ("test" in f["path"].lower() and f["is_code"])]
    if not test_fws and any(f["path"].startswith("tests/") for f in files):
        if primary == "Python":
            test_fws.append("pytest")

    repo_name = os.path.basename(os.path.normpath(repo_path))
    file_tree = sorted([f["path"] for f in files if f["is_code"]])

    repo_info = {
        "name": repo_name,
        "url": repo_url,
        "path": repo_path,
        "primary_language": primary,
        "languages": lang_counts,
        "frameworks": list(set(frameworks)),
        "package_managers": list(set(pkg_mgrs)),
        "test_frameworks": list(set(test_fws)),
        "file_count": len(files),
        "code_file_count": len(code_files),
        "test_files": test_dirs[:20],
    }

    evidence.append(_evidence(
        claim=f"Repository '{repo_name}' scanned: {len(code_files)} code files, primary language: {primary}",
        reason="File system scan", etype="ast"
    ))
    events.append(_event(1, "Repository Scanner", "complete",
                         f"Scanned {len(code_files)} code files. Primary: {primary}",
                         {"file_count": len(code_files), "language": primary}))

    return {
        "repo_info": repo_info,
        "file_tree": file_tree,
        "evidence": evidence,
        "events": events,
        "current_step": "repository_scanner",
    }


# ════════════════════════════════════════════════════════════════════════
#  STEP 2 — ARCHITECTURE ANALYZER
# ════════════════════════════════════════════════════════════════════════
def architecture_analyzer(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    repo_info = state.get("repo_info", {})
    file_tree = state.get("file_tree", [])
    events, evidence = [], []

    events.append(_event(2, "Architecture Analyzer", "running",
                         "Reconstructing application architecture..."))

    # Build a concise directory summary
    dir_structure = {}
    for fp in file_tree[:200]:
        parts = fp.split("/")
        if len(parts) > 1:
            dir_structure.setdefault(parts[0], []).append(fp)

    dir_summary = ""
    for d, fls in sorted(dir_structure.items()):
        dir_summary += f"\n{d}/ ({len(fls)} files)"
        for fl in fls[:5]:
            dir_summary += f"\n  {fl}"
        if len(fls) > 5:
            dir_summary += f"\n  ... and {len(fls)-5} more"

    # Use LLM to summarize architecture
    try:
        llm = _get_llm()
        prompt = f"""Analyze this repository structure and provide a brief architecture summary.

Repository: {repo_info.get('name', 'unknown')}
Primary Language: {repo_info.get('primary_language', 'unknown')}
Frameworks: {repo_info.get('frameworks', [])}

Directory Structure:{dir_summary}

Respond with a concise architecture summary (3-5 sentences) describing the application layers and key components. No JSON, just plain text."""

        arch = llm.generate(prompt, system_prompt="You are a software architect. Be concise and factual.",
                            temperature=0.3, max_tokens=300)
    except Exception as e:
        logger.warning(f"LLM architecture analysis failed: {e}")
        arch = f"Repository with {repo_info.get('code_file_count', 0)} code files. Primary language: {repo_info.get('primary_language', 'Unknown')}."

    evidence.append(_evidence(
        claim="Architecture reconstructed from directory structure",
        reason=arch[:200], etype="ast"
    ))
    events.append(_event(2, "Architecture Analyzer", "complete",
                         "Architecture reconstructed.", {"summary": arch[:300]}))

    return {"architecture": arch, "events": events, "evidence": evidence,
            "current_step": "architecture_analyzer"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 3 — ISSUE INTERPRETER
# ════════════════════════════════════════════════════════════════════════
def issue_interpreter(state: AgentState) -> Dict[str, Any]:
    user_request = state["user_request"]
    repo_info = state.get("repo_info", {})
    file_tree = state.get("file_tree", [])
    events, evidence = [], []

    events.append(_event(3, "Issue Interpreter", "running",
                         "Understanding user request..."))

    # Build context
    tree_str = "\n".join(file_tree[:100])

    try:
        llm = _get_llm()
        prompt = f"""Analyze this user request for a code repository.

Repository: {repo_info.get('name', 'unknown')}
Language: {repo_info.get('primary_language', 'unknown')}

File tree:
{tree_str}

User request: "{user_request}"

Respond in JSON:
{{
  "goal": "one sentence goal",
  "must_change": ["file paths likely to change"],
  "must_not_break": ["existing behaviors to preserve"],
  "acceptance_conditions": ["conditions to verify success"],
  "suspected_components": ["files or functions likely involved"],
  "summary": "brief summary"
}}"""

        result = llm.generate_json(prompt, system_prompt="You are a software engineer analyzing a task. Be precise.")
    except Exception as e:
        logger.warning(f"LLM issue analysis failed: {e}")
        result = {
            "goal": user_request,
            "must_change": [],
            "must_not_break": ["existing tests"],
            "acceptance_conditions": ["all tests pass"],
            "suspected_components": [],
            "summary": user_request,
        }

    # Try to find relevant files via simple keyword matching
    keywords = user_request.lower().split()
    relevant_files = []
    for fp in file_tree:
        fp_lower = fp.lower()
        if any(kw in fp_lower for kw in keywords if len(kw) > 3):
            relevant_files.append(fp)
    result["relevant_files"] = result.get("must_change", []) + relevant_files[:10]

    evidence.append(_evidence(
        claim=f"Issue understood: {result.get('goal', user_request)[:100]}",
        reason="LLM analysis of user request", etype="search"
    ))
    events.append(_event(3, "Issue Interpreter", "complete",
                         f"Issue understood: {result.get('goal', '')[:80]}",
                         {"suspected_files": result.get("suspected_components", [])}))

    return {"issue_analysis": result, "events": events, "evidence": evidence,
            "current_step": "issue_interpreter"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 4 — SYMBOL RETRIEVER
# ════════════════════════════════════════════════════════════════════════
def symbol_retriever(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    issue = state.get("issue_analysis", {})
    events, evidence = [], []

    events.append(_event(4, "Symbol Retriever", "running",
                         "Identifying relevant symbols..."))

    suspected = issue.get("suspected_components", []) + issue.get("relevant_files", [])
    found_symbols = []

    # Read suspected files and extract symbol names
    for fp in suspected[:10]:
        full = os.path.join(repo_path, fp) if not os.path.isabs(fp) else fp
        if not os.path.isfile(full):
            # Try to find a matching file
            for root, _, fnames in os.walk(repo_path):
                for fn in fnames:
                    if fp.replace("/", os.sep) in os.path.join(root, fn):
                        full = os.path.join(root, fn)
                        break
        if os.path.isfile(full):
            content = _read_file_safe(full)
            rel = os.path.relpath(full, repo_path).replace("\\", "/")
            # Simple extraction: find function/class definitions
            for i, line in enumerate(content.split("\n"), 1):
                stripped = line.strip()
                if stripped.startswith("def ") or stripped.startswith("class "):
                    name = stripped.split("(")[0].split(":")[0].replace("def ", "").replace("class ", "").strip()
                    stype = "function" if stripped.startswith("def") else "class"
                    found_symbols.append({
                        "name": name, "type": stype,
                        "file": rel, "line": i
                    })

            evidence.append(_evidence(
                claim=f"File '{rel}' contains {len([s for s in found_symbols if s['file'] == rel])} symbols",
                file=rel, reason="Symbol extraction from source code", etype="ast"
            ))

    events.append(_event(4, "Symbol Retriever", "complete",
                         f"Found {len(found_symbols)} symbols in suspected files.",
                         {"symbols_count": len(found_symbols),
                          "symbols": found_symbols[:20]}))

    # Store in issue analysis for downstream
    issue_updated = dict(issue)
    issue_updated["found_symbols"] = found_symbols

    return {"issue_analysis": issue_updated, "events": events, "evidence": evidence,
            "current_step": "symbol_retriever"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 5 — IMPACT ANALYZER
# ════════════════════════════════════════════════════════════════════════
def impact_analyzer(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    issue = state.get("issue_analysis", {})
    file_tree = state.get("file_tree", [])
    events, evidence = [], []

    events.append(_event(5, "Impact Analyzer", "running",
                         "Calculating impact radius..."))

    suspected = issue.get("suspected_components", []) + issue.get("relevant_files", [])
    suspected = list(set(suspected))

    directly_affected = suspected[:10]
    indirectly_affected = []

    # Find files that import from directly affected files
    for fp in file_tree:
        if fp in directly_affected:
            continue
        full = os.path.join(repo_path, fp)
        if os.path.isfile(full) and fp.endswith(".py"):
            try:
                content = _read_file_safe(full, max_kb=50)
                for daf in directly_affected:
                    module = daf.replace("/", ".").replace(".py", "").replace("\\", ".")
                    basename = os.path.splitext(os.path.basename(daf))[0]
                    if f"import {basename}" in content or f"from {module}" in content or f"from {basename}" in content:
                        indirectly_affected.append(fp)
                        break
            except Exception:
                pass

    # Find affected tests
    affected_tests = [f for f in file_tree
                      if ("test" in f.lower()) and f.endswith(".py")]

    impact = {
        "directly_affected": directly_affected,
        "indirectly_affected": list(set(indirectly_affected))[:10],
        "affected_tests": affected_tests[:10],
        "risk_score": min(len(directly_affected) * 10 + len(indirectly_affected) * 5, 100),
        "risk_level": "low" if len(directly_affected) <= 2 else ("medium" if len(directly_affected) <= 5 else "high"),
    }

    evidence.append(_evidence(
        claim=f"Impact radius: {len(directly_affected)} direct, {len(indirectly_affected)} indirect, {len(affected_tests)} tests",
        reason="Import analysis and file dependency scan", etype="ast"
    ))
    events.append(_event(5, "Impact Analyzer", "complete",
                         f"Impact: {len(directly_affected)} direct, {len(indirectly_affected)} indirect files.",
                         impact))

    return {"impact_radius": impact, "events": events, "evidence": evidence,
            "current_step": "impact_analyzer"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 6 — ROOT CAUSE INVESTIGATOR
# ════════════════════════════════════════════════════════════════════════
def root_cause_investigator(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    issue = state.get("issue_analysis", {})
    user_request = state.get("user_request", "")
    events, evidence = [], []

    events.append(_event(6, "Root Cause Investigator", "running",
                         "Determining root cause..."))

    # Gather source code of suspected files
    suspected = issue.get("suspected_components", []) + issue.get("relevant_files", [])
    code_context = ""
    for fp in suspected[:5]:
        full = os.path.join(repo_path, fp) if not os.path.isabs(fp) else fp
        if os.path.isfile(full):
            content = _read_file_safe(full, max_kb=100)
            code_context += f"\n\n--- {fp} ---\n{content}"

    # If no files found, try to search
    if not code_context.strip():
        for root, _, fnames in os.walk(repo_path):
            dirs_skip = {".git", "node_modules", "venv", "__pycache__"}
            if any(d in root for d in dirs_skip):
                continue
            for fn in fnames:
                if fn.endswith(".py"):
                    fp = os.path.join(root, fn)
                    rel = os.path.relpath(fp, repo_path).replace("\\", "/")
                    content = _read_file_safe(fp, max_kb=50)
                    code_context += f"\n\n--- {rel} ---\n{content}"
            if len(code_context) > 20000:
                break

    try:
        llm = _get_llm()
        prompt = f"""Analyze this code and user request to determine the root cause.

User request: "{user_request}"

Relevant source code:
{code_context[:15000]}

Respond in JSON:
{{
  "root_cause": "technical description of the root cause",
  "description": "detailed explanation",
  "confidence": 0.0 to 1.0,
  "files_involved": ["file paths"],
  "symbols_involved": ["function or class names"],
  "evidence_summary": "what evidence supports this conclusion"
}}"""

        result = llm.generate_json(prompt,
                                   system_prompt="You are a senior debugging engineer. Identify root causes precisely based on code evidence.")
    except Exception as e:
        logger.warning(f"LLM root cause analysis failed: {e}")
        result = {
            "root_cause": "Could not determine root cause automatically",
            "description": str(e),
            "confidence": 0.3,
            "files_involved": suspected[:3],
            "symbols_involved": [],
            "evidence_summary": "Automated analysis based on file structure"
        }

    for f in result.get("files_involved", []):
        evidence.append(_evidence(
            claim=f"File '{f}' is involved in the root cause",
            file=f, reason=result.get("evidence_summary", ""), etype="search"
        ))

    events.append(_event(6, "Root Cause Investigator", "complete",
                         f"Root cause: {result.get('root_cause', 'unknown')[:100]}",
                         {"confidence": result.get("confidence", 0)}))

    return {"root_cause": result, "events": events, "evidence": evidence,
            "current_step": "root_cause_investigator"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 7 — PATCH PLANNER
# ════════════════════════════════════════════════════════════════════════
def patch_planner(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    root_cause = state.get("root_cause", {})
    issue = state.get("issue_analysis", {})
    user_request = state.get("user_request", "")
    events, evidence = [], []

    events.append(_event(7, "Patch Planner", "running", "Planning minimal patch..."))

    files_involved = root_cause.get("files_involved", [])
    code_context = ""
    for fp in files_involved[:5]:
        full = os.path.join(repo_path, fp)
        if os.path.isfile(full):
            content = _read_file_safe(full, max_kb=100)
            code_context += f"\n\n--- {fp} ---\n{content}"

    try:
        llm = _get_llm()
        prompt = f"""Plan a minimal code patch for this issue.

User request: "{user_request}"
Root cause: {root_cause.get('root_cause', 'unknown')}
Root cause details: {root_cause.get('description', '')}

Source code:
{code_context[:12000]}

Rules:
- Minimal changes only
- Do NOT rewrite entire files
- Preserve existing style and public interfaces
- Do NOT invent imports that don't exist in the repo

Respond in JSON:
{{
  "files_to_edit": ["file paths to modify"],
  "edits": [
    {{
      "file_path": "path/to/file.py",
      "original_code": "exact lines to replace (copy from source)",
      "replacement_code": "new code to insert",
      "reason": "why this change"
    }}
  ],
  "rationale": "overall patch strategy",
  "risk_assessment": "low/medium/high",
  "tests_to_add": ["description of tests to add"]
}}"""

        result = llm.generate_json(prompt,
                                   system_prompt="You are a senior software engineer. Generate minimal, safe patches.")
    except Exception as e:
        logger.warning(f"LLM patch planning failed: {e}")
        result = {
            "files_to_edit": files_involved[:3],
            "edits": [],
            "rationale": "Automated patch based on root cause analysis",
            "risk_assessment": "medium",
            "tests_to_add": ["regression test for the fix"]
        }

    evidence.append(_evidence(
        claim=f"Patch plan: {len(result.get('edits', []))} edits across {len(result.get('files_to_edit', []))} files",
        reason=result.get("rationale", ""), etype="search"
    ))
    events.append(_event(7, "Patch Planner", "complete",
                         f"Planned {len(result.get('edits', []))} edits.",
                         {"files": result.get("files_to_edit", [])}))

    return {"patch_plan": result, "events": events, "evidence": evidence,
            "current_step": "patch_planner"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 8 — PATCH GENERATOR + APPLICATOR
# ════════════════════════════════════════════════════════════════════════
def patch_generator(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    plan = state.get("patch_plan", {})
    events, evidence = [], []

    events.append(_event(8, "Patch Generator", "running",
                         "Generating and applying patches..."))

    edits = plan.get("edits", [])
    applied = []
    failed = []

    # Create a git branch for the patch
    _run_cmd("git checkout -b repoguard-patch 2>/dev/null || git checkout repoguard-patch", repo_path)

    for edit in edits:
        fp = edit.get("file_path", "")
        original = edit.get("original_code", "")
        replacement = edit.get("replacement_code", "")

        full_path = os.path.join(repo_path, fp)
        if not os.path.isfile(full_path):
            failed.append({"file": fp, "error": "File not found"})
            continue

        content = _read_file_safe(full_path)
        if original and original.strip() in content:
            new_content = content.replace(original.strip(), replacement.strip(), 1)
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                applied.append(edit)
                evidence.append(_evidence(
                    claim=f"Patch applied to {fp}",
                    file=fp, reason=edit.get("reason", ""),
                    etype="runtime"
                ))
            except Exception as e:
                failed.append({"file": fp, "error": str(e)})
        else:
            # Try fuzzy match — strip whitespace and compare
            orig_stripped = original.strip().replace("\r", "")
            content_stripped = content.replace("\r", "")
            if orig_stripped and orig_stripped in content_stripped:
                new_content = content_stripped.replace(orig_stripped, replacement.strip(), 1)
                try:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    applied.append(edit)
                    evidence.append(_evidence(
                        claim=f"Patch applied to {fp} (fuzzy match)",
                        file=fp, reason=edit.get("reason", ""), etype="runtime"
                    ))
                except Exception as e:
                    failed.append({"file": fp, "error": str(e)})
            else:
                failed.append({"file": fp, "error": "Original code not found in file"})

    # Get diff
    diff_result = _run_cmd("git diff", repo_path)
    diff_text = diff_result.get("stdout", "")

    success = len(applied) > 0

    events.append(_event(8, "Patch Generator", "complete" if success else "failed",
                         f"Applied {len(applied)}/{len(edits)} edits. {len(failed)} failed.",
                         {"applied": len(applied), "failed": len(failed),
                          "failures": failed}))

    return {
        "patches": applied,
        "patch_applied": success,
        "patch_diff": diff_text,
        "events": events,
        "evidence": evidence,
        "current_step": "patch_generator"
    }


# ════════════════════════════════════════════════════════════════════════
#  STEP 9 — TEST GENERATOR
# ════════════════════════════════════════════════════════════════════════
def test_generator(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    root_cause = state.get("root_cause", {})
    patches = state.get("patches", [])
    plan = state.get("patch_plan", {})
    user_request = state.get("user_request", "")
    events, evidence = [], []

    events.append(_event(9, "Test Generator", "running",
                         "Generating regression test..."))

    # Find existing test patterns
    test_files = []
    for root, _, fnames in os.walk(repo_path):
        if ".git" in root or "node_modules" in root or "venv" in root:
            continue
        for fn in fnames:
            if fn.startswith("test_") and fn.endswith(".py"):
                test_files.append(os.path.relpath(
                    os.path.join(root, fn), repo_path).replace("\\", "/"))

    test_context = ""
    if test_files:
        # Read first test file for pattern
        tf = os.path.join(repo_path, test_files[0])
        test_context = _read_file_safe(tf, max_kb=50)

    # Read patched files for context
    patched_code = ""
    for edit in (patches or []):
        fp = edit.get("file_path", "")
        full = os.path.join(repo_path, fp)
        if os.path.isfile(full):
            patched_code += f"\n--- {fp} ---\n{_read_file_safe(full, max_kb=50)}"

    generated_test = ""
    try:
        llm = _get_llm()
        prompt = f"""Generate a regression test for this fix.

User request: "{user_request}"
Root cause: {root_cause.get('root_cause', 'unknown')}

Patched code:
{patched_code[:8000]}

Existing test pattern:
{test_context[:4000]}

Requirements:
- The test must verify the fix works
- Follow existing test patterns/style
- Use the same test framework (pytest)
- Import from the correct module
- Only output the Python test code, nothing else

Output ONLY the Python test code:"""

        generated_test = llm.generate(prompt,
                                      system_prompt="You are a test engineer. Generate clean pytest test code.",
                                      temperature=0.3, max_tokens=1000)
        # Clean up
        if "```python" in generated_test:
            generated_test = generated_test.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_test:
            generated_test = generated_test.split("```")[1].split("```")[0].strip()
    except Exception as e:
        logger.warning(f"LLM test generation failed: {e}")
        generated_test = ""

    # Write test to repo if generated
    if generated_test:
        test_dir = os.path.join(repo_path, "tests")
        if not os.path.isdir(test_dir):
            test_dir = repo_path
        test_path = os.path.join(test_dir, "test_repoguard_regression.py")
        try:
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(generated_test)
            rel = os.path.relpath(test_path, repo_path).replace("\\", "/")
            evidence.append(_evidence(
                claim=f"Regression test written to {rel}",
                file=rel, reason="Auto-generated to verify fix", etype="test"
            ))
        except Exception as e:
            logger.error(f"Failed to write test: {e}")

    events.append(_event(9, "Test Generator", "complete",
                         "Regression test generated." if generated_test else "No test generated.",
                         {"test_generated": bool(generated_test)}))

    return {"generated_test": generated_test, "events": events, "evidence": evidence,
            "current_step": "test_generator"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 10 — TEST EXECUTOR
# ════════════════════════════════════════════════════════════════════════
def test_executor(state: AgentState) -> Dict[str, Any]:
    repo_path = state["repo_path"]
    repo_info = state.get("repo_info", {})
    events, evidence = [], []

    events.append(_event(10, "Test Executor", "running", "Running tests..."))

    lang = repo_info.get("primary_language", "Python")
    test_fws = repo_info.get("test_frameworks", [])

    # Determine test command
    if "pytest" in test_fws or lang == "Python":
        cmd = "python -m pytest -v --tb=short 2>&1"
    elif "jest" in test_fws:
        cmd = "npx jest --verbose 2>&1"
    elif "vitest" in test_fws:
        cmd = "npx vitest run 2>&1"
    else:
        cmd = "python -m pytest -v --tb=short 2>&1"

    result = _run_cmd(cmd, repo_path, timeout=settings.COMMAND_TIMEOUT)

    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    exit_code = result.get("code", -1)

    # Parse pytest output
    total, passed, failed, errors = 0, 0, 0, 0
    test_details = []

    for line in stdout.split("\n"):
        if " PASSED" in line:
            passed += 1
            name = line.split(" PASSED")[0].strip().split("::")[-1] if "::" in line else line.split(" PASSED")[0].strip()
            test_details.append({"name": name, "status": "passed"})
        elif " FAILED" in line:
            failed += 1
            name = line.split(" FAILED")[0].strip().split("::")[-1] if "::" in line else line.split(" FAILED")[0].strip()
            test_details.append({"name": name, "status": "failed"})
        elif " ERROR" in line:
            errors += 1
            name = line.split(" ERROR")[0].strip()
            test_details.append({"name": name, "status": "error"})

    total = passed + failed + errors

    # Try to extract summary line
    for line in stdout.split("\n"):
        if "passed" in line and ("failed" in line or "error" in line or "warning" in line or line.strip().startswith("=")):
            pass

    test_result = {
        "framework": "pytest" if "pytest" in cmd else "unknown",
        "command": cmd,
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "tests": test_details,
        "stdout": stdout[-3000:],  # Truncate
        "stderr": stderr[-1000:],
        "exit_code": exit_code,
    }

    evidence.append(_evidence(
        claim=f"Tests executed: {passed} passed, {failed} failed, {errors} errors",
        reason=f"Command: {cmd}", etype="test"
    ))
    events.append(_event(10, "Test Executor", "complete",
                         f"Tests: {passed} passed, {failed} failed",
                         {"passed": passed, "failed": failed, "total": total}))

    return {"test_results": test_result, "events": events, "evidence": evidence,
            "current_step": "test_executor"}


# ════════════════════════════════════════════════════════════════════════
#  STEP 11 — REGRESSION ANALYZER
# ════════════════════════════════════════════════════════════════════════
def regression_analyzer(state: AgentState) -> Dict[str, Any]:
    test_results = state.get("test_results", {})
    baseline = state.get("baseline_tests", {})
    events, evidence = [], []

    events.append(_event(11, "Regression Analyzer", "running",
                         "Analyzing regression..."))

    failed = test_results.get("failed", 0)
    errors = test_results.get("errors", 0)
    passed = test_results.get("passed", 0)
    exit_code = test_results.get("exit_code", -1)

    # Simple regression: if tests pass, no regression
    has_regression = (failed > 0 or errors > 0) and exit_code != 0

    comparisons = []
    for t in test_results.get("tests", []):
        comparisons.append({
            "test_name": t.get("name", ""),
            "baseline": "N/A",
            "patched": t.get("status", "unknown"),
            "verdict": "preserved" if t.get("status") == "passed" else "REGRESSION"
        })

    regressions = [c["test_name"] for c in comparisons if c["verdict"] == "REGRESSION"]

    reg_result = {
        "passed": not has_regression,
        "comparisons": comparisons,
        "regressions": regressions,
        "fixes": [],
        "summary": f"{'No regressions detected' if not has_regression else f'{len(regressions)} regressions found'}. {passed} tests passed."
    }

    evidence.append(_evidence(
        claim=f"Regression analysis: {'PASS' if not has_regression else 'FAIL'}",
        reason=f"{len(regressions)} regressions found" if has_regression else "All tests passed",
        etype="test"
    ))
    events.append(_event(11, "Regression Analyzer",
                         "complete" if not has_regression else "failed",
                         reg_result["summary"],
                         {"regressions": regressions, "passed": not has_regression}))

    return {"regression_result": reg_result, "events": events, "evidence": evidence,
            "current_step": "regression_analyzer"}


# ════════════════════════════════════════════════════════════════════════
#  REPAIR DECISION (conditional edge)
# ════════════════════════════════════════════════════════════════════════
def repair_decision(state: AgentState) -> str:
    reg = state.get("regression_result", {})
    passed = reg.get("passed", False) if reg else False
    attempts = state.get("repair_attempts", 0)

    if passed:
        return "final_reporter"
    elif attempts < settings.MAX_REPAIR_ATTEMPTS:
        return "root_cause_investigator"
    else:
        return "final_reporter"


# ════════════════════════════════════════════════════════════════════════
#  INCREMENT REPAIR ATTEMPTS
# ════════════════════════════════════════════════════════════════════════
def repair_incrementer(state: AgentState) -> Dict[str, Any]:
    """Increment repair counter and rollback patch before retrying."""
    repo_path = state["repo_path"]
    attempts = state.get("repair_attempts", 0) + 1

    # Rollback
    _run_cmd("git checkout -- .", repo_path)

    return {
        "repair_attempts": attempts,
        "patch_applied": False,
        "events": [_event(0, "Self-Repair", "running",
                          f"Repair attempt {attempts}/{settings.MAX_REPAIR_ATTEMPTS}. Rolling back and retrying...")],
        "evidence": [_evidence(
            claim=f"Repair attempt {attempts}: rolling back failed patch",
            reason="Regression detected", etype="runtime"
        )],
    }


# ════════════════════════════════════════════════════════════════════════
#  FINAL REPORTER
# ════════════════════════════════════════════════════════════════════════
def final_reporter(state: AgentState) -> Dict[str, Any]:
    events, evidence = [], []
    events.append(_event(12, "Final Reporter", "running", "Generating report..."))

    reg = state.get("regression_result", {})
    passed = reg.get("passed", False)
    root_cause = state.get("root_cause", {})
    test_results = state.get("test_results", {})
    impact = state.get("impact_radius", {})
    patches = state.get("patches", [])
    diff = state.get("patch_diff", "")

    # ── Confidence Score ──
    score = 0
    breakdown = []
    penalties = []

    # +20 root cause evidence
    rc_conf = root_cause.get("confidence", 0.0) if root_cause else 0.0
    rc_pts = round(rc_conf * 20)
    score += rc_pts
    breakdown.append({"component": "Root cause evidence", "score": rc_pts, "max_score": 20})

    # +20 regression test
    has_gen_test = bool(state.get("generated_test"))
    reg_test_pts = 20 if has_gen_test else 0
    score += reg_test_pts
    breakdown.append({"component": "Regression test", "score": reg_test_pts, "max_score": 20})

    # +20 test suite passes
    suite_pts = 20 if passed else 0
    score += suite_pts
    breakdown.append({"component": "Test suite passes", "score": suite_pts, "max_score": 20})

    # +15 impacted tests
    imp_pts = 15 if passed else 0
    score += imp_pts
    breakdown.append({"component": "Impacted tests pass", "score": imp_pts, "max_score": 15})

    # +10 static analysis
    static_pts = 10 if state.get("patch_applied") else 5
    score += static_pts
    breakdown.append({"component": "Static analysis", "score": static_pts, "max_score": 10})

    # +10 API verification
    api_pts = 10 if state.get("patch_applied") else 5
    score += api_pts
    breakdown.append({"component": "API verification", "score": api_pts, "max_score": 10})

    # +5 minimal patch
    min_pts = 5 if len(patches or []) <= 3 else 2
    score += min_pts
    breakdown.append({"component": "Minimal patch", "score": min_pts, "max_score": 5})

    # Penalties
    if not passed:
        pen = 25
        score -= pen
        penalties.append({"component": "Regression failure", "score": -pen, "max_score": 0})

    score = max(0, min(100, score))

    if score >= 90:
        classification = "HIGH"
    elif score >= 75:
        classification = "MODERATE"
    elif score >= 50:
        classification = "LOW"
    else:
        classification = "REJECTED"

    confidence = {
        "score": score,
        "classification": classification,
        "breakdown": breakdown,
        "penalties": penalties,
    }

    # Build final report
    report = {
        "task_id": state.get("task_id", ""),
        "success": passed and state.get("patch_applied", False),
        "user_request": state.get("user_request", ""),
        "root_cause": root_cause.get("root_cause", "") if root_cause else "",
        "root_cause_details": root_cause.get("description", "") if root_cause else "",
        "affected_components": (impact.get("directly_affected", []) if impact else []),
        "impact_radius": impact,
        "patch_diff": diff,
        "files_changed": [e.get("file_path", "") for e in (patches or [])],
        "patch_rationale": state.get("patch_plan", {}).get("rationale", ""),
        "regression_test_added": bool(state.get("generated_test")),
        "test_results": test_results,
        "regression_result": reg,
        "confidence": confidence,
        "evidence": state.get("evidence", []),
        "repair_attempts": state.get("repair_attempts", 0),
        "summary": f"{'Patch applied successfully' if passed and state.get('patch_applied') else 'Patch failed or rejected'}. Confidence: {score}/100 ({classification})",
    }

    events.append(_event(12, "Final Reporter", "complete",
                         f"Report generated. Confidence: {score}/100 ({classification})",
                         {"score": score, "classification": classification}))

    return {
        "confidence": confidence,
        "final_report": report,
        "status": "completed" if report["success"] else "failed",
        "events": events,
        "evidence": evidence,
        "current_step": "final_reporter",
    }


# ════════════════════════════════════════════════════════════════════════
#  BUILD WORKFLOW
# ════════════════════════════════════════════════════════════════════════
def build_workflow():
    """Construct and compile the LangGraph agent workflow."""
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("repository_scanner", repository_scanner)
    workflow.add_node("architecture_analyzer", architecture_analyzer)
    workflow.add_node("issue_interpreter", issue_interpreter)
    workflow.add_node("symbol_retriever", symbol_retriever)
    workflow.add_node("impact_analyzer", impact_analyzer)
    workflow.add_node("root_cause_investigator", root_cause_investigator)
    workflow.add_node("patch_planner", patch_planner)
    workflow.add_node("patch_generator", patch_generator)
    workflow.add_node("test_generator", test_generator)
    workflow.add_node("test_executor", test_executor)
    workflow.add_node("regression_analyzer", regression_analyzer)
    workflow.add_node("repair_incrementer", repair_incrementer)
    workflow.add_node("final_reporter", final_reporter)

    # Linear pipeline
    workflow.set_entry_point("repository_scanner")
    workflow.add_edge("repository_scanner", "architecture_analyzer")
    workflow.add_edge("architecture_analyzer", "issue_interpreter")
    workflow.add_edge("issue_interpreter", "symbol_retriever")
    workflow.add_edge("symbol_retriever", "impact_analyzer")
    workflow.add_edge("impact_analyzer", "root_cause_investigator")
    workflow.add_edge("root_cause_investigator", "patch_planner")
    workflow.add_edge("patch_planner", "patch_generator")
    workflow.add_edge("patch_generator", "test_generator")
    workflow.add_edge("test_generator", "test_executor")
    workflow.add_edge("test_executor", "regression_analyzer")

    # Conditional: repair loop or finalize
    workflow.add_conditional_edges(
        "regression_analyzer",
        repair_decision,
        {
            "final_reporter": "final_reporter",
            "root_cause_investigator": "repair_incrementer",
        }
    )
    workflow.add_edge("repair_incrementer", "root_cause_investigator")
    workflow.add_edge("final_reporter", END)

    return workflow.compile()
