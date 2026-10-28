from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import hashlib
import json


def _fingerprint(assessment: Dict[str, Any]) -> str:
    stable = json.dumps(assessment, sort_keys=True, default=str)
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def save_release_assessment(
    assessment: Dict[str, Any],
    output_dir: str = "outputs",
) -> Dict[str, Any]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fingerprint = _fingerprint(assessment)
    index_path = Path(output_dir) / "assessment_index.json"

    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            index = {}
    else:
        index = {}

    if fingerprint in index:
        existing_file = index[fingerprint]["file"]
        return {
            "saved": True,
            "duplicate": True,
            "assessment_id": index[fingerprint]["assessment_id"],
            "file": existing_file,
            "deployment_triggered": False,
        }

    assessment_id = fingerprint[:12]
    record = dict(assessment)
    record["assessment_id"] = assessment_id
    record["created_at"] = datetime.now().isoformat()
    record["deployment_triggered"] = False
    record["evidence_references"] = [
        "data/tests.csv",
        "data/defects.csv",
        "data/security_findings.json",
        "data/release_criteria.txt",
    ]

    filename = f"assessment_{assessment_id}.json"
    file_path = Path(output_dir) / filename
    file_path.write_text(
        json.dumps(record, indent=2, default=str),
        encoding="utf-8",
    )

    index[fingerprint] = {
        "assessment_id": assessment_id,
        "file": str(file_path),
    }
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    return {
        "saved": True,
        "duplicate": False,
        "assessment_id": assessment_id,
        "file": str(file_path),
        "deployment_triggered": False,
    }
