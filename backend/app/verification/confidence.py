from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class ConfidenceScore:
    score: int
    classification: str
    breakdown: Dict[str, int]

class ConfidenceEngine:
    def __init__(self):
        pass

    def calculate(self, metrics: Dict[str, Any]) -> ConfidenceScore:
        score = 0
        breakdown = {}

        # Bonuses
        if metrics.get("root_cause_supported"):
            score += 20
            breakdown["root_cause_supported"] = 20
        if metrics.get("regression_test_passes"):
            score += 20
            breakdown["regression_test_passes"] = 20
        if metrics.get("existing_test_suite_passes"):
            score += 20
            breakdown["existing_test_suite_passes"] = 20
        if metrics.get("impacted_tests_pass"):
            score += 15
            breakdown["impacted_tests_pass"] = 15
        if metrics.get("static_analysis_passes"):
            score += 10
            breakdown["static_analysis_passes"] = 10
        if metrics.get("api_verification_passes"):
            score += 10
            breakdown["api_verification_passes"] = 10
        if metrics.get("minimal_patch_score"):
            score += 5
            breakdown["minimal_patch_score"] = 5

        # Penalties
        if metrics.get("unrelated_files_changed"):
            score -= 20
            breakdown["unrelated_files_changed"] = -20
        if metrics.get("new_dependency_without_justification"):
            score -= 20
            breakdown["new_dependency_without_justification"] = -20
        if metrics.get("regression_failure"):
            score -= 25
            breakdown["regression_failure"] = -25
        if metrics.get("unverified_api_usage"):
            score -= 25
            breakdown["unverified_api_usage"] = -25
        if metrics.get("test_coverage_weakened"):
            score -= 15
            breakdown["test_coverage_weakened"] = -15

        # Cap score between 0 and 100
        score = max(0, min(100, score))

        classification = "REJECT"
        if score >= 90:
            classification = "HIGH"
        elif score >= 75:
            classification = "MODERATE"
        elif score >= 50:
            classification = "LOW"

        return ConfidenceScore(
            score=score,
            classification=classification,
            breakdown=breakdown
        )
