from typing import TypedDict, Optional, List, Annotated
from app.models import (
    RepositoryInfo, IssueAnalysis, RootCauseAnalysis, ImpactRadius,
    PatchPlan, CodeEdit, TestResult, RegressionResult, EvidenceRecord,
    ConfidenceScore, FinalReport, AgentEvent
)
import operator

class AgentState(TypedDict):
    task_id: str
    repo_path: str
    repo_info: Optional[RepositoryInfo]
    user_request: str
    issue_analysis: Optional[IssueAnalysis]
    root_cause: Optional[RootCauseAnalysis]
    impact_radius: Optional[ImpactRadius]
    patch_plan: Optional[PatchPlan]
    patches: List[CodeEdit]
    patch_applied: bool
    test_results: Optional[TestResult]
    baseline_tests: Optional[TestResult]
    regression_result: Optional[RegressionResult]
    evidence: Annotated[List[EvidenceRecord], operator.add]
    confidence: Optional[ConfidenceScore]
    final_report: Optional[FinalReport]
    repair_attempts: int
    current_step: str
    events: Annotated[List[AgentEvent], operator.add]
    error: Optional[str]
    status: str
