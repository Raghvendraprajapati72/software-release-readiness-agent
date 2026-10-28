from datetime import datetime

from agent.gates import evaluate_release_gates
from agent.readers import read_criteria
from agent.storage import save_release_assessment
from agent.tools import (
    calculate_test_pass_rate,
    check_evidence_freshness,
    check_security_findings,
    get_blocking_defects,
)


def run_release_assessment(
    test_file: str = "data/tests.csv",
    defect_file: str = "data/defects.csv",
    security_file: str = "data/security_findings.json",
    criteria_file: str = "data/release_criteria.txt",
    minimum_pass_rate: float = 95.0,
    max_age_hours: float = 24.0,
    conditional_allowed: bool = False,
):
    test_result = calculate_test_pass_rate(test_file)
    defect_result = get_blocking_defects(defect_file)
    security_result = check_security_findings(security_file)

    # Use the newest test execution timestamp as the evidence freshness signal.
    try:
        import pandas as pd
        tests = pd.read_csv(test_file)
        if tests.empty or "executed_at" not in tests.columns:
            freshness_result = {
                "fresh": False,
                "status": "FAIL",
                "age_hours": None,
                "max_allowed_hours": max_age_hours,
                "reason": "Test evidence timestamp is missing.",
            }
        else:
            timestamps = pd.to_datetime(tests["executed_at"], errors="coerce").dropna()
            if timestamps.empty:
                freshness_result = {
                    "fresh": False,
                    "status": "FAIL",
                    "age_hours": None,
                    "max_allowed_hours": max_age_hours,
                    "reason": "No valid test evidence timestamp found.",
                }
            else:
                latest = timestamps.max().to_pydatetime().replace(tzinfo=None)
                freshness_result = check_evidence_freshness(
                    latest.isoformat(),
                    max_age_hours=max_age_hours,
                )
    except Exception as exc:
        freshness_result = {
            "fresh": False,
            "status": "FAIL",
            "age_hours": None,
            "max_allowed_hours": max_age_hours,
            "reason": f"Could not evaluate evidence freshness: {exc}",
        }

    criteria_text = read_criteria(criteria_file)

    gate_result = evaluate_release_gates(
        test_result,
        defect_result,
        security_result,
        freshness_result,
        minimum_pass_rate=minimum_pass_rate,
        conditional_allowed=conditional_allowed,
    )

    assessment = {
        "test_results": test_result,
        "defect_results": defect_result,
        "security_results": security_result,
        "freshness_result": freshness_result,
        "release_criteria": criteria_text,
        "release_decision": gate_result["decision"],
        "gates": gate_result["gates"],
        "failed_mandatory_gates": gate_result["failed_mandatory_gates"],
        "human_approval_required": True,
        "deployment_triggered": False,
    }

    save_result = save_release_assessment(assessment)

    return assessment, save_result


def print_report(assessment, save_result):
    print("\n" + "=" * 60)
    print("SOFTWARE RELEASE READINESS ASSESSMENT")
    print("=" * 60)

    print(f"Test Pass Rate   : {assessment['test_results'].get('pass_rate')}%")
    print(f"Passed Tests     : {assessment['test_results'].get('passed')}")
    print(f"Failed Tests     : {assessment['test_results'].get('failed')}")
    print(f"Blocking Defects : {assessment['defect_results'].get('count')}")
    print(f"Security Issues  : {assessment['security_results'].get('count')}")
    print(f"Evidence Age     : {assessment['freshness_result'].get('age_hours')} hours")

    print("\nRELEASE GATES")
    print("-" * 60)
    for gate in assessment["gates"]:
        icon = "PASS" if gate["passed"] else "FAIL"
        print(
            f"[{icon}] {gate['gate']} | "
            f"Required: {gate['required']} | "
            f"Actual: {gate['actual']}"
        )

    print("\n" + "=" * 60)
    print(f"FINAL RECOMMENDATION: {assessment['release_decision']}")
    print("=" * 60)
    print(f"Human approval required : {assessment['human_approval_required']}")
    print(f"Deployment triggered     : {assessment['deployment_triggered']}")
    print(f"Assessment file          : {save_result['file']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    assessment, save_result = run_release_assessment()
    print_report(assessment, save_result)
