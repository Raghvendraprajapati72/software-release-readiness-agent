from pathlib import Path
import json

import pandas as pd

from agent.tools import (
    calculate_test_pass_rate,
    check_evidence_freshness,
    check_security_findings,
    get_blocking_defects,
)


def test_pass_rate(tmp_path: Path):
    path = tmp_path / "tests.csv"
    pd.DataFrame([
        {"test_id": "T1", "status": "PASS"},
        {"test_id": "T2", "status": "PASS"},
        {"test_id": "T3", "status": "FAIL"},
        {"test_id": "T4", "status": "PASS"},
    ]).to_csv(path, index=False)

    result = calculate_test_pass_rate(str(path))
    assert result["pass_rate"] == 75.0
    assert result["total"] == 4
    assert result["status"] == "PASS"


def test_missing_test_evidence():
    result = calculate_test_pass_rate("does-not-exist.csv")
    assert result["status"] == "FAIL"
    assert result["evidence_available"] is False


def test_blocking_defects(tmp_path: Path):
    path = tmp_path / "defects.csv"
    pd.DataFrame([
        {"defect_id": "D1", "severity": "CRITICAL", "status": "OPEN"},
        {"defect_id": "D2", "severity": "LOW", "status": "OPEN"},
        {"defect_id": "D3", "severity": "HIGH", "status": "CLOSED"},
    ]).to_csv(path, index=False)

    result = get_blocking_defects(str(path))
    assert result["count"] == 1
    assert result["defects"] == ["D1"]
    assert result["status"] == "FAIL"


def test_security_findings(tmp_path: Path):
    path = tmp_path / "security.json"
    path.write_text(json.dumps([
        {"id": "S1", "severity": "HIGH", "status": "OPEN"},
        {"id": "S2", "severity": "LOW", "status": "OPEN"},
    ]), encoding="utf-8")

    result = check_security_findings(str(path))
    assert result["count"] == 1
    assert result["status"] == "FAIL"


def test_freshness():
    result = check_evidence_freshness(
        "2026-10-27T10:00:00",
        max_age_hours=24,
    )
    # The exact current time varies, so only validate structure.
    assert "fresh" in result
    assert "age_hours" in result
