from datetime import datetime
from typing import Any, Dict
import json

import pandas as pd

from .validators import validate_file_exists


def calculate_test_pass_rate(file_path: str = "data/tests.csv") -> Dict[str, Any]:
    validation = validate_file_exists(file_path)
    if not validation["available"]:
        return {
            "pass_rate": 0.0,
            "passed": 0,
            "failed": 0,
            "total": 0,
            "status": "FAIL",
            "evidence_available": False,
            "reason": validation["reason"],
        }

    df = pd.read_csv(file_path)
    if df.empty:
        return {
            "pass_rate": 0.0,
            "passed": 0,
            "failed": 0,
            "total": 0,
            "status": "FAIL",
            "evidence_available": False,
            "reason": "No test evidence was executed.",
        }

    if "status" not in df.columns:
        return {
            "pass_rate": 0.0,
            "passed": 0,
            "failed": 0,
            "total": 0,
            "status": "FAIL",
            "evidence_available": False,
            "reason": "Required column 'status' is missing.",
        }

    statuses = df["status"].fillna("").astype(str).str.upper().str.strip()
    total = len(df)
    passed = int((statuses == "PASS").sum())
    failed = total - passed

    # Zero-executed evidence is always a failure.
    if total == 0:
        return {
            "pass_rate": 0.0,
            "passed": 0,
            "failed": 0,
            "total": 0,
            "status": "FAIL",
            "evidence_available": False,
            "reason": "Zero tests were executed.",
        }

    pass_rate = round((passed / total) * 100, 2)

    return {
        "pass_rate": pass_rate,
        "passed": passed,
        "failed": failed,
        "total": total,
        "status": "PASS",
        "evidence_available": True,
        "reason": "Test evidence processed successfully.",
    }


def get_blocking_defects(
    file_path: str = "data/defects.csv",
) -> Dict[str, Any]:
    validation = validate_file_exists(file_path)
    if not validation["available"]:
        return {
            "count": 0,
            "defects": [],
            "status": "FAIL",
            "evidence_available": False,
            "reason": validation["reason"],
        }

    df = pd.read_csv(file_path)
    required = {"defect_id", "severity", "status"}
    if not required.issubset(df.columns):
        return {
            "count": 0,
            "defects": [],
            "status": "FAIL",
            "evidence_available": False,
            "reason": f"Missing required columns: {sorted(required - set(df.columns))}",
        }

    severity = df["severity"].fillna("").astype(str).str.upper().str.strip()
    status = df["status"].fillna("").astype(str).str.upper().str.strip()

    blocking = df[
        severity.isin({"CRITICAL", "HIGH"}) &
        status.eq("OPEN")
    ]

    return {
        "count": int(len(blocking)),
        "defects": blocking["defect_id"].astype(str).tolist(),
        "status": "PASS" if len(blocking) == 0 else "FAIL",
        "evidence_available": True,
        "reason": "Blocking defect analysis completed.",
    }


def check_security_findings(
    file_path: str = "data/security_findings.json",
) -> Dict[str, Any]:
    validation = validate_file_exists(file_path)
    if not validation["available"]:
        return {
            "count": 0,
            "findings": [],
            "status": "FAIL",
            "evidence_available": False,
            "reason": validation["reason"],
        }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            findings = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "count": 0,
            "findings": [],
            "status": "FAIL",
            "evidence_available": False,
            "reason": f"Could not read security evidence: {exc}",
        }

    if not isinstance(findings, list) or not findings:
        return {
            "count": 0,
            "findings": [],
            "status": "FAIL",
            "evidence_available": False,
            "reason": "Security evidence is missing or empty.",
        }

    blocking = []
    for finding in findings:
        severity = str(finding.get("severity", "")).upper().strip()
        status = str(finding.get("status", "")).upper().strip()
        if severity in {"CRITICAL", "HIGH"} and status == "OPEN":
            blocking.append(finding)

    return {
        "count": len(blocking),
        "findings": blocking,
        "status": "PASS" if len(blocking) == 0 else "FAIL",
        "evidence_available": True,
        "reason": "Security finding analysis completed.",
    }


def check_evidence_freshness(
    timestamp: str,
    max_age_hours: float = 24,
    now: datetime | None = None,
) -> Dict[str, Any]:
    try:
        evidence_time = datetime.fromisoformat(timestamp)
    except ValueError:
        return {
            "fresh": False,
            "status": "FAIL",
            "age_hours": None,
            "reason": "Invalid evidence timestamp.",
        }

    current = now or datetime.now()
    age_hours = (current - evidence_time).total_seconds() / 3600

    # Future timestamps are suspicious and fail the gate.
    fresh = 0 <= age_hours <= max_age_hours

    return {
        "fresh": fresh,
        "status": "PASS" if fresh else "FAIL",
        "age_hours": round(age_hours, 2),
        "max_allowed_hours": max_age_hours,
        "reason": "Evidence is fresh." if fresh else "Evidence is stale or invalid.",
    }
