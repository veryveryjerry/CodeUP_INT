from dataclasses import dataclass
from typing import Dict, List, Any
from .executor import TestResult

@dataclass
class RegressionResult:
    analysis: List[Dict[str, str]]
    has_regressions: bool
    has_fixes: bool

class RegressionAnalyzer:
    def __init__(self):
        pass

    def analyze(self, baseline: TestResult, post_patch: TestResult) -> RegressionResult:
        """Compares baseline test results vs post-patch results."""
        analysis = []
        has_regressions = False
        has_fixes = False

        baseline_map = {t["name"]: t["status"] for t in baseline.test_details}
        post_patch_map = {t["name"]: t["status"] for t in post_patch.test_details}

        all_tests = set(baseline_map.keys()).union(set(post_patch_map.keys()))

        for test in all_tests:
            b_status = baseline_map.get(test, "MISSING")
            p_status = post_patch_map.get(test, "MISSING")
            
            verdict = "UNCHANGED"
            if b_status == "passed" and p_status == "failed":
                verdict = "REGRESSION"
                has_regressions = True
            elif b_status == "failed" and p_status == "passed":
                verdict = "FIXED"
                has_fixes = True
            elif b_status == "MISSING" and p_status != "MISSING":
                verdict = "NEW"
            
            analysis.append({
                "test_name": test,
                "baseline_status": b_status,
                "patched_status": p_status,
                "verdict": verdict
            })

        return RegressionResult(
            analysis=analysis,
            has_regressions=has_regressions,
            has_fixes=has_fixes
        )
