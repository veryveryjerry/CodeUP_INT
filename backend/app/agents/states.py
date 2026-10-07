"""LangGraph agent states for RepoGuard AI."""
from typing import TypedDict, Optional, List, Annotated, Dict, Any
import operator


class AgentState(TypedDict):
    # Task context
    task_id: str
    repo_url: str
    repo_path: str
    user_request: str

    # Repository analysis
    repo_info: Optional[Dict[str, Any]]
    architecture: Optional[str]
    file_tree: Optional[List[str]]

    # Issue understanding
    issue_analysis: Optional[Dict[str, Any]]

    # Root cause
    root_cause: Optional[Dict[str, Any]]

    # Impact
    impact_radius: Optional[Dict[str, Any]]

    # Planning
    patch_plan: Optional[Dict[str, Any]]

    # Patching
    patches: Optional[List[Dict[str, Any]]]
    patch_applied: bool
    patch_diff: Optional[str]

    # Testing
    baseline_tests: Optional[Dict[str, Any]]
    test_results: Optional[Dict[str, Any]]
    regression_result: Optional[Dict[str, Any]]
    generated_test: Optional[str]

    # Verification
    confidence: Optional[Dict[str, Any]]
    static_analysis: Optional[Dict[str, Any]]

    # Evidence
    evidence: Annotated[List[Dict[str, Any]], operator.add]

    # Report
    final_report: Optional[Dict[str, Any]]

    # Control flow
    repair_attempts: int
    current_step: str
    status: str
    error: Optional[str]

    # Events for SSE streaming
    events: Annotated[List[Dict[str, Any]], operator.add]
