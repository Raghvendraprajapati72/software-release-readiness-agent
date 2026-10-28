from agent.gates import evaluate_release_gates


def passing_test():
    return {
        "evidence_available": True,
        "total": 100,
        "pass_rate": 98,
    }


def passing_defects():
    return {
        "evidence_available": True,
        "count": 0,
    }


def passing_security():
    return {
        "evidence_available": True,
        "count": 0,
    }


def passing_freshness():
    return {
        "fresh": True,
        "age_hours": 2,
        "max_allowed_hours": 24,
    }


def test_go_when_all_gates_pass():
    result = evaluate_release_gates(
        passing_test(),
        passing_defects(),
        passing_security(),
        passing_freshness(),
    )
    assert result["decision"] == "GO"


def test_no_go_when_test_gate_fails():
    test = passing_test()
    test["pass_rate"] = 80

    result = evaluate_release_gates(
        test,
        passing_defects(),
        passing_security(),
        passing_freshness(),
    )
    assert result["decision"] == "NO-GO"


def test_conditional_go_when_policy_allows():
    test = passing_test()
    test["pass_rate"] = 90

    result = evaluate_release_gates(
        test,
        passing_defects(),
        passing_security(),
        passing_freshness(),
        conditional_allowed=True,
    )
    assert result["decision"] == "CONDITIONAL-GO"


def test_missing_evidence_is_failure():
    test = passing_test()
    test["evidence_available"] = False

    result = evaluate_release_gates(
        test,
        passing_defects(),
        passing_security(),
        passing_freshness(),
    )
    assert result["decision"] == "NO-GO"
