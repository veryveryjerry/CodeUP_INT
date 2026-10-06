import logging
import datetime
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from app.models import (
    RepositoryInfo, IssueAnalysis, RootCauseAnalysis, ImpactRadius,
    PatchPlan, EvidenceRecord, ConfidenceScore, FinalReport, AgentEvent
)
from app.agents.states import AgentState
from app.agents.tools import repo_scan, record_evidence
from app.patching.generator import PatchGenerator
from app.patching.applier import PatchApplier

logger = logging.getLogger(__name__)

def create_event(msg: str) -> AgentEvent:
    return AgentEvent(timestamp=datetime.datetime.now().isoformat(), message=msg)

def repository_scanner(state: AgentState) -> Dict[str, Any]:
    repo_info = RepositoryInfo(path=state["repo_path"], file_count=100) # mock
    evt = create_event("Scanned repository")
    evd = EvidenceRecord(type="scan", data={"info": "scan complete"})
    return {"repo_info": repo_info, "events": [evt], "evidence": [evd], "current_step": "repository_scanner"}

def architecture_analyzer(state: AgentState) -> Dict[str, Any]:
    evt = create_event("Analyzed architecture")
    return {"events": [evt], "current_step": "architecture_analyzer"}

def issue_interpreter(state: AgentState) -> Dict[str, Any]:
    # Mock LLM call for issue interpreter
    analysis = IssueAnalysis(summary="Analyzed request", severity="high", affected_components=["core"], expected_behavior="fix", actual_behavior="bug")
    evt = create_event("Interpreted issue")
    return {"issue_analysis": analysis, "events": [evt], "current_step": "issue_interpreter"}

def symbol_retriever(state: AgentState) -> Dict[str, Any]:
    evt = create_event("Retrieved symbols")
    return {"events": [evt], "current_step": "symbol_retriever"}

def impact_analyzer(state: AgentState) -> Dict[str, Any]:
    impact = ImpactRadius(files=["main.py"], risk_level="low")
    evt = create_event("Analyzed impact")
    return {"impact_radius": impact, "events": [evt], "current_step": "impact_analyzer"}

def root_cause_investigator(state: AgentState) -> Dict[str, Any]:
    rc = RootCauseAnalysis(description="Found root cause", files_involved=["main.py"], confidence=0.9)
    evt = create_event("Investigated root cause")
    return {"root_cause": rc, "events": [evt], "current_step": "root_cause_investigator"}

def patch_planner(state: AgentState) -> Dict[str, Any]:
    plan = PatchPlan(strategy="Replace logic", steps=[{"file": "main.py", "action": "update", "description": "fix loop"}], risk_assessment="low")
    evt = create_event("Planned patch")
    return {"patch_plan": plan, "events": [evt], "current_step": "patch_planner"}

def patch_generator(state: AgentState) -> Dict[str, Any]:
    generator = PatchGenerator()
    # Mocking generation
    # edits = generator.generate_edits(...) 
    edits = []
    evt = create_event("Generated patch edits")
    return {"patches": edits, "events": [evt], "current_step": "patch_generator"}

def patch_validator(state: AgentState) -> Dict[str, Any]:
    applier = PatchApplier(state["repo_path"])
    # mock applying
    applied = True
    evt = create_event("Validated and applied patch")
    return {"patch_applied": applied, "events": [evt], "current_step": "patch_validator"}

def test_generator(state: AgentState) -> Dict[str, Any]:
    evt = create_event("Generated regression tests")
    return {"events": [evt], "current_step": "test_generator"}

def test_executor(state: AgentState) -> Dict[str, Any]:
    evt = create_event("Executed tests")
    return {"events": [evt], "current_step": "test_executor"}

def regression_analyzer(state: AgentState) -> Dict[str, Any]:
    evt = create_event("Analyzed regression")
    # simulate result
    class MockResult: pass
    res = MockResult()
    res.passed = True
    return {"regression_result": res, "events": [evt], "current_step": "regression_analyzer"}

def repair_decision(state: AgentState) -> str:
    res = state.get("regression_result")
    passed = getattr(res, "passed", False) if res else False
    if passed:
        return "final_reporter"
    else:
        if state["repair_attempts"] < 5:
            return "root_cause_investigator"
        return "final_reporter"

def final_reporter(state: AgentState) -> Dict[str, Any]:
    report = FinalReport(summary="Process finished", issue_resolved=True, patch_applied=state["patch_applied"], tests_passed=True)
    evt = create_event("Generated final report")
    return {"final_report": report, "status": "completed", "events": [evt], "current_step": "final_reporter"}


def build_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("repository_scanner", repository_scanner)
    workflow.add_node("architecture_analyzer", architecture_analyzer)
    workflow.add_node("issue_interpreter", issue_interpreter)
    workflow.add_node("symbol_retriever", symbol_retriever)
    workflow.add_node("impact_analyzer", impact_analyzer)
    workflow.add_node("root_cause_investigator", root_cause_investigator)
    workflow.add_node("patch_planner", patch_planner)
    workflow.add_node("patch_generator", patch_generator)
    workflow.add_node("patch_validator", patch_validator)
    workflow.add_node("test_generator", test_generator)
    workflow.add_node("test_executor", test_executor)
    workflow.add_node("regression_analyzer", regression_analyzer)
    workflow.add_node("final_reporter", final_reporter)
    
    workflow.set_entry_point("repository_scanner")
    
    workflow.add_edge("repository_scanner", "architecture_analyzer")
    workflow.add_edge("architecture_analyzer", "issue_interpreter")
    workflow.add_edge("issue_interpreter", "symbol_retriever")
    workflow.add_edge("symbol_retriever", "impact_analyzer")
    workflow.add_edge("impact_analyzer", "root_cause_investigator")
    workflow.add_edge("root_cause_investigator", "patch_planner")
    workflow.add_edge("patch_planner", "patch_generator")
    workflow.add_edge("patch_generator", "patch_validator")
    workflow.add_edge("patch_validator", "test_generator")
    workflow.add_edge("test_generator", "test_executor")
    workflow.add_edge("test_executor", "regression_analyzer")
    
    workflow.add_conditional_edges(
        "regression_analyzer",
        repair_decision,
        {
            "final_reporter": "final_reporter",
            "root_cause_investigator": "root_cause_investigator"
        }
    )
    
    workflow.add_edge("final_reporter", END)
    
    return workflow.compile()
