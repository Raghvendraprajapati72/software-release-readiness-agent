from pathlib import Path
from typing import Any, Dict


def validate_file_exists(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return {
            "available": False,
            "status": "FAIL",
            "reason": f"Evidence file not found: {file_path}",
        }
    return {
        "available": True,
        "status": "PASS",
        "reason": "Evidence file is available.",
    }


def require_evidence(data: Any, source: str) -> Dict[str, Any]:
    if data is None:
        return {
            "available": False,
            "status": "FAIL",
            "reason": f"Evidence missing: {source}",
        }
    if hasattr(data, "empty") and data.empty:
        return {
            "available": False,
            "status": "FAIL",
            "reason": f"Evidence is empty: {source}",
        }
    if isinstance(data, (list, dict)) and len(data) == 0:
        return {
            "available": False,
            "status": "FAIL",
            "reason": f"Evidence is empty: {source}",
        }
    return {
        "available": True,
        "status": "PASS",
        "reason": "Evidence is present.",
    }
