from agent.storage import save_release_assessment


def test_duplicate_safe_save(tmp_path):
    assessment = {
        "release_decision": "GO",
        "deployment_triggered": False,
    }

    first = save_release_assessment(assessment, str(tmp_path))
    second = save_release_assessment(assessment, str(tmp_path))

    assert first["saved"] is True
    assert second["saved"] is True
    assert second["duplicate"] is True
    assert first["assessment_id"] == second["assessment_id"]
    assert second["deployment_triggered"] is False
