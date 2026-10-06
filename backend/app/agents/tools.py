import os
import subprocess
import glob
from typing import List, Dict, Any, Optional
from app.models import EvidenceRecord
from app.patching.applier import PatchApplier

def repo_scan(repo_path: str) -> Dict[str, Any]:
    """scan repository"""
    return {"files_count": sum(len(files) for _, _, files in os.walk(repo_path))}

def read_file(file_path: str) -> str:
    """read file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def read_symbol(file_path: str, symbol_name: str) -> str:
    """extract specific symbol (simplified)"""
    return f"Symbol {symbol_name} from {file_path}"

def search_code(query: str, repo_path: str) -> List[str]:
    """keyword search"""
    # Simplified search
    results = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.py', '.ts', '.js')):
                try:
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        if query in f.read():
                            results.append(path)
                except Exception:
                    pass
    return results

def search_semantic(query: str, repo_path: str) -> List[str]:
    """semantic search"""
    return [f"Semantic match for {query}"]

def get_dependency_graph(repo_path: str) -> Dict[str, List[str]]:
    """get graph data"""
    return {"moduleA": ["moduleB"]}

def get_callers(symbol_name: str, repo_path: str) -> List[str]:
    """find callers"""
    return [f"Caller of {symbol_name}"]

def get_callees(symbol_name: str, repo_path: str) -> List[str]:
    """find callees"""
    return [f"Callee of {symbol_name}"]

def find_tests(repo_path: str) -> List[str]:
    """discover tests"""
    return glob.glob(os.path.join(repo_path, "tests", "**", "*.py"), recursive=True)

def get_git_history(file_path: str, n: int = 5) -> str:
    """recent commits"""
    try:
        result = subprocess.run(
            ["git", "log", f"-n{n}", "--oneline", file_path],
            cwd=os.path.dirname(file_path),
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return str(e)

def run_command(cmd: str, cwd: str, timeout: int = 30) -> str:
    """execute command"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return str(e)

def run_tests(test_cmd: str, cwd: str) -> Dict[str, Any]:
    """run tests"""
    output = run_command(test_cmd, cwd)
    return {"passed": "FAILED" not in output, "output": output}

def apply_patch(edits: List[Any], repo_path: str) -> bool:
    """apply code changes"""
    applier = PatchApplier(repo_path)
    # applier.create_branch()  # usually handled outside
    return applier.apply_edits(edits)

def git_diff(repo_path: str) -> str:
    """get diff"""
    applier = PatchApplier(repo_path)
    return applier.generate_diff()

def rollback_patch(repo_path: str) -> bool:
    """rollback changes"""
    applier = PatchApplier(repo_path)
    return applier.rollback()

def record_evidence(evidence: EvidenceRecord) -> EvidenceRecord:
    """add to ledger"""
    return evidence
