from typing import Any, Dict, List


def evaluate_release_gates(
    test_result: Dict[str, Any],
    defect_result: Dict[str, Any],
    security_result: Dict[str, Any],
    freshness_result: Dict[str, Any],
    minimum_pass_rate: float = 95.0,
    conditional_allowed: bool = False,
) -> Dict[str, Any]:
    gates: List[Dict[str, Any]] = []

    test_pass = (
        test_result.get("evidence_available", False)
        and test_result.get("total", 0) > 0
        and test_result.get("pass_rate", 0) >= minimum_pass_rate
    )
    gates.append({
        "gate": "Test Pass Rate",
        "required": f">= {minimum_pass_rate}%",
        "actual": test_result.get("pass_rate", 0),
        "passed": test_pass,
        "mandatory": True,
    })

    defect_pass = (
        defect_result.get("evidence_available", False)
        and defect_result.get("count") == 0
    )
    gates.append({
        "gate": "Blocking Defects",
        "required": "0 open CRITICAL/HIGH defects",
        "actual": defect_result.get("count", 0),
        "passed": defect_pass,
        "mandatory": True,
    })

    security_pass = (
        security_result.get("evidence_available", False)
        and security_result.get("count") == 0
    )
    gates.append({
        "gate": "Security Findings",
        "required": "0 open CRITICAL/HIGH findings",
        "actual": security_result.get("count", 0),
        "passed": security_pass,
        "mandatory": True,
    })

    freshness_pass = freshness_result.get("fresh", False)
    gates.append({
        "gate": "Evidence Freshness",
        "required": f"<= {freshness_result.get('max_allowed_hours', 24)} hours",
        "actual": freshness_result.get("age_hours"),
        "passed": freshness_pass,
        "mandatory": True,
    })

    failed_mandatory = [g for g in gates if g["mandatory"] and not g["passed"]]

    if not failed_mandatory:
        decision = "GO"
    elif conditional_allowed:
        decision = "CONDITIONAL-GO"
    else:
        decision = "NO-GO"

    return {
        "decision": decision,
        "gates": gates,
        "failed_mandatory_gates": [g["gate"] for g in failed_mandatory],
        "deployment_triggered": False,
    }
