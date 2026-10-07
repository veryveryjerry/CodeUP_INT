"""Pydantic models for RepoGuard AI."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


# ─── Enums ───────────────────────────────────────────────────────────────
class SymbolType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    EXPORT = "export"
    DECORATOR = "decorator"
    ENDPOINT = "endpoint"
    TEST = "test"


class EvidenceType(str, Enum):
    AST = "ast"
    SEARCH = "search"
    TEST = "test"
    RUNTIME = "runtime"
    GIT = "git"
    MANIFEST = "manifest"
    STATIC = "static"


class PatchConfidence(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    REJECTED = "REJECTED"


class TaskState(str, Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    ANALYZING = "analyzing"
    UNDERSTANDING = "understanding"
    PLANNING = "planning"
    PATCHING = "patching"
    TESTING = "testing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


# ─── Core Models ─────────────────────────────────────────────────────────
class RepositoryInfo(BaseModel):
    id: str = ""
    url: str = ""
    name: str = ""
    path: str = ""
    branch: str = "main"
    commit_hash: Optional[str] = None
    primary_language: str = "Unknown"
    languages: Dict[str, int] = Field(default_factory=dict)
    frameworks: List[str] = Field(default_factory=list)
    package_managers: List[str] = Field(default_factory=list)
    test_frameworks: List[str] = Field(default_factory=list)
    build_systems: List[str] = Field(default_factory=list)
    file_count: int = 0
    total_lines: int = 0
    architecture_summary: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FileInfo(BaseModel):
    path: str
    language: str = ""
    extension: str = ""
    size: int = 0
    lines: int = 0
    hash: str = ""


class SymbolInfo(BaseModel):
    id: str = ""
    file_path: str
    name: str
    type: SymbolType
    start_line: int = 0
    end_line: int = 0
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None


class RelationshipInfo(BaseModel):
    source_id: str
    target_id: str
    type: str  # imports, calls, inherits, tested_by, etc.
    source_file: str = ""
    target_file: str = ""


# ─── Task Models ─────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    repo_url: str
    issue_description: str


class TaskStatus(BaseModel):
    id: str
    repo_url: str = ""
    issue_description: str = ""
    state: TaskState = TaskState.PENDING
    progress: float = 0.0
    message: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TimelineStep(BaseModel):
    step: int
    name: str
    description: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None


# ─── Analysis Models ─────────────────────────────────────────────────────
class IssueAnalysis(BaseModel):
    goal: str = ""
    must_change: List[str] = Field(default_factory=list)
    must_not_break: List[str] = Field(default_factory=list)
    acceptance_conditions: List[str] = Field(default_factory=list)
    suspected_components: List[str] = Field(default_factory=list)
    summary: str = ""
    relevant_files: List[str] = Field(default_factory=list)


class RootCauseAnalysis(BaseModel):
    description: str = ""
    root_cause: str = ""
    confidence: float = 0.0
    files_involved: List[str] = Field(default_factory=list)
    symbols_involved: List[str] = Field(default_factory=list)
    evidence_summary: str = ""


# ─── Patch Models ────────────────────────────────────────────────────────
class CodeEdit(BaseModel):
    file_path: str
    original_code: str
    replacement_code: str
    reason: str = ""
    start_line: Optional[int] = None
    end_line: Optional[int] = None


class PatchPlan(BaseModel):
    files_to_edit: List[str] = Field(default_factory=list)
    symbols_to_edit: List[str] = Field(default_factory=list)
    rationale: str = ""
    edits: List[CodeEdit] = Field(default_factory=list)
    risk_assessment: str = "low"
    rollback_strategy: str = "git reset --hard HEAD"
    tests_to_add: List[str] = Field(default_factory=list)
    existing_tests_to_run: List[str] = Field(default_factory=list)


class PatchResult(BaseModel):
    success: bool = False
    applied_edits: int = 0
    files_changed: List[str] = Field(default_factory=list)
    diff: str = ""
    error: Optional[str] = None


class PatchCost(BaseModel):
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    public_interfaces_changed: int = 0
    dependency_changes: int = 0
    risk_score: float = 0.0
    total: float = 0.0


# ─── Test Models ─────────────────────────────────────────────────────────
class TestDetail(BaseModel):
    name: str
    status: str  # passed, failed, error, skipped
    duration: float = 0.0
    output: str = ""
    error_message: Optional[str] = None


class TestResult(BaseModel):
    framework: str = ""
    command: str = ""
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration: float = 0.0
    tests: List[TestDetail] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1


class RegressionComparison(BaseModel):
    test_name: str
    baseline: str  # PASS, FAIL, N/A
    patched: str   # PASS, FAIL, N/A
    verdict: str   # preserved, fixed, REGRESSION, unresolved, new_pass, new_fail


class RegressionResult(BaseModel):
    passed: bool = False
    comparisons: List[RegressionComparison] = Field(default_factory=list)
    regressions: List[str] = Field(default_factory=list)
    fixes: List[str] = Field(default_factory=list)
    summary: str = ""


# ─── Evidence Models ─────────────────────────────────────────────────────
class EvidenceRecord(BaseModel):
    claim: str = ""
    file: str = ""
    symbol: str = ""
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    reason: str = ""
    evidence_type: EvidenceType = EvidenceType.AST
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Impact Models ───────────────────────────────────────────────────────
class ImpactRadius(BaseModel):
    directly_affected: List[str] = Field(default_factory=list)
    indirectly_affected: List[str] = Field(default_factory=list)
    affected_tests: List[str] = Field(default_factory=list)
    risk_score: float = 0.0
    risk_level: str = "low"


# ─── Confidence Models ──────────────────────────────────────────────────
class ConfidenceBreakdown(BaseModel):
    component: str
    score: float
    max_score: float
    reason: str = ""


class ConfidenceScore(BaseModel):
    score: float = 0.0
    classification: PatchConfidence = PatchConfidence.REJECTED
    breakdown: List[ConfidenceBreakdown] = Field(default_factory=list)
    penalties: List[ConfidenceBreakdown] = Field(default_factory=list)


# ─── Report Models ──────────────────────────────────────────────────────
class FinalReport(BaseModel):
    task_id: str = ""
    success: bool = False
    user_request: str = ""
    root_cause: str = ""
    affected_components: List[str] = Field(default_factory=list)
    impact_radius: Optional[ImpactRadius] = None
    patch_diff: str = ""
    files_changed: List[str] = Field(default_factory=list)
    lines_changed: int = 0
    patch_rationale: str = ""
    regression_test_added: str = ""
    test_results: Optional[TestResult] = None
    regression_result: Optional[RegressionResult] = None
    confidence: Optional[ConfidenceScore] = None
    evidence: List[EvidenceRecord] = Field(default_factory=list)
    timeline: List[TimelineStep] = Field(default_factory=list)
    summary: str = ""
    repair_attempts: int = 0


class TaskResult(BaseModel):
    task_id: str
    report: FinalReport


# ─── SSE Event ───────────────────────────────────────────────────────────
class AgentEvent(BaseModel):
    type: str  # step_start, step_complete, step_failed, log, progress, result
    step: Optional[int] = None
    step_name: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Graph Visualization ────────────────────────────────────────────────
class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # file, function, class, test
    file: str = ""
    line: int = 0
    impact: str = "none"  # none, direct, indirect


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # imports, calls, inherits, tested_by


class DependencyGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
