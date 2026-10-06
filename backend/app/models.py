from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class SymbolType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"

class EvidenceType(str, Enum):
    TEST_PASS = "test_pass"
    TEST_FAIL = "test_fail"
    LINT_PASS = "lint_pass"
    LOG_MATCH = "log_match"
    DOC_REFERENCE = "doc_reference"

class PatchConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskState(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    REPRODUCING = "reproducing"
    PATCHING = "patching"
    TESTING = "testing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"

class RepositoryInfo(BaseModel):
    id: str
    url: str
    branch: str
    commit_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FileInfo(BaseModel):
    path: str
    language: str
    size: int
    lines: int

class SymbolInfo(BaseModel):
    id: str
    file_path: str
    name: str
    type: SymbolType
    start_line: int
    end_line: int

class RelationshipInfo(BaseModel):
    source_id: str
    target_id: str
    type: str

class TaskCreate(BaseModel):
    repo_url: str
    issue_description: str

class TaskStatus(BaseModel):
    id: str
    state: TaskState
    progress: float
    message: str
    created_at: datetime

class IssueAnalysis(BaseModel):
    summary: str
    relevant_files: List[str]

class RootCauseAnalysis(BaseModel):
    cause: str
    evidence: str

class CodeEdit(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    original_code: str
    replacement_code: str

class PatchPlan(BaseModel):
    edits: List[CodeEdit]
    rationale: str

class PatchResult(BaseModel):
    success: bool
    applied_edits: int

class TestResult(BaseModel):
    test_name: str
    passed: bool
    output: str
    duration: float

class RegressionResult(BaseModel):
    passed: bool
    failed_tests: List[TestResult]

class EvidenceRecord(BaseModel):
    type: EvidenceType
    description: str
    score: float

class EvidenceLedger(BaseModel):
    records: List[EvidenceRecord]
    total_score: float

class ImpactRadius(BaseModel):
    files_affected: List[str]
    symbols_affected: List[str]

class ConfidenceScore(BaseModel):
    score: float
    factors: List[str]

class FinalReport(BaseModel):
    task_id: str
    success: bool
    summary: str
    patch_diff: Optional[str] = None

class TaskResult(BaseModel):
    task_id: str
    report: FinalReport

class AgentEvent(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
