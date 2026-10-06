ISSUE_ANALYSIS_PROMPT = """You are an expert software engineer analyzing a bug or feature request.
Analyze the request and provide a structured JSON response matching this schema:
{
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "Brief summary of the issue"},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "affected_components": {"type": "array", "items": {"type": "string"}},
        "expected_behavior": {"type": "string"},
        "actual_behavior": {"type": "string"}
    },
    "required": ["summary", "severity", "affected_components"]
}

Issue:
{issue_text}
"""

ROOT_CAUSE_PROMPT = """Analyze the code and evidence to determine the root cause of the issue.
Return JSON matching this schema:
{
    "type": "object",
    "properties": {
        "description": {"type": "string", "description": "Detailed explanation of the root cause"},
        "files_involved": {"type": "array", "items": {"type": "string"}},
        "functions_involved": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["description", "files_involved", "confidence"]
}

Code Context:
{code_context}

Evidence:
{evidence}
"""

PATCH_PLAN_PROMPT = """Create a patch plan based on the root cause analysis.
Return JSON matching this schema:
{
    "type": "object",
    "properties": {
        "strategy": {"type": "string", "description": "Overall strategy to fix the issue"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "action": {"type": "string", "enum": ["create", "update", "delete"]},
                    "description": {"type": "string"}
                },
                "required": ["file", "action", "description"]
            }
        },
        "risk_assessment": {"type": "string"}
    },
    "required": ["strategy", "steps", "risk_assessment"]
}

Root Cause:
{root_cause}
"""

CODE_EDIT_PROMPT = """Generate specific code edits for the file to implement the plan.
Return JSON matching this schema:
{
    "type": "object",
    "properties": {
        "edits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "old_content": {"type": "string", "description": "Exact text to replace, must exist in original file"},
                    "new_content": {"type": "string", "description": "Text to replace it with"},
                    "reason": {"type": "string"}
                },
                "required": ["old_content", "new_content", "reason"]
            }
        }
    },
    "required": ["edits"]
}

Plan:
{plan}

Original File Content ({file_path}):
{file_content}
"""

TEST_GENERATION_PROMPT = """Generate regression tests for the implemented patch.
Return JSON matching this schema:
{
    "type": "object",
    "properties": {
        "test_code": {"type": "string", "description": "Complete test file content"},
        "test_file_path": {"type": "string", "description": "Path where the test should be written"},
        "framework": {"type": "string"}
    },
    "required": ["test_code", "test_file_path"]
}

Patch:
{patch_content}
"""

VERIFICATION_PROMPT = """Verify the applied patch correctness.
Return JSON matching this schema:
{
    "type": "object",
    "properties": {
        "is_correct": {"type": "boolean"},
        "issues_found": {"type": "array", "items": {"type": "string"}},
        "recommendation": {"type": "string"}
    },
    "required": ["is_correct", "issues_found"]
}

Original issue:
{issue}

Applied patch:
{patch}
"""

ARCHITECTURE_PROMPT = """Summarize the repository architecture.
Return JSON matching this schema:
{
    "type": "object",
    "properties": {
        "overview": {"type": "string"},
        "key_components": {"type": "array", "items": {"type": "string"}},
        "patterns_used": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["overview", "key_components"]
}

Repository Data:
{repo_data}
"""

FINAL_REPORT_PROMPT = """Generate a final evidence-backed report.
Return JSON matching this schema:
{
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "issue_resolved": {"type": "boolean"},
        "patch_applied": {"type": "boolean"},
        "tests_passed": {"type": "boolean"},
        "details": {"type": "string"},
        "evidence_summary": {"type": "string"}
    },
    "required": ["summary", "issue_resolved", "patch_applied", "tests_passed"]
}

State data:
{state_data}
"""
