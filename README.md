# Software Release Readiness Decision Support Agent

HCL Career Shaper-style Project 04: Decision Support.

This project analyzes release evidence and produces an advisory GO / NO-GO /
CONDITIONAL-GO recommendation. It never deploys software.

## Features
- Test pass-rate calculation with zero-division protection
- Blocking defect detection
- Security finding checks
- Evidence freshness checks
- Release-gate evaluation
- Missing evidence treated as failure
- Conditional-GO policy support
- Idempotent/duplicate-safe assessment saves
- CSV, JSON, PDF and DOCX evidence readers
- Pytest test suite
- Human-in-the-loop / responsible-AI guardrails

## Project structure

```text
software-release-readiness-agent/
├── agent/
│   ├── __init__.py
│   ├── tools.py
│   ├── gates.py
│   ├── validators.py
│   ├── readers.py
│   └── storage.py
├── data/
│   ├── tests.csv
│   ├── defects.csv
│   ├── security_findings.json
│   ├── release_criteria.txt
│   └── release_criteria.docx
├── tests/
│   ├── test_tools.py
│   ├── test_gates.py
│   └── test_storage.py
├── outputs/
├── main.py
├── requirements.txt
└── README.md
```

## Run

### 1. Create environment
Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the assessment
```bash
python main.py
```

### 4. Run tests
```bash
pytest -q
```

## Decision policy

Default mandatory gates:
- Test pass rate >= 95%
- Open CRITICAL/HIGH defects = 0
- Open CRITICAL/HIGH security findings = 0
- Evidence freshness <= 24 hours

Missing or zero-executed test evidence is a failure.

`CONDITIONAL-GO` is only returned when the caller explicitly allows it and
there are no mandatory hard blockers under the selected policy.

## Responsible AI

The agent is advisory only. A human release manager owns the final decision
and deployment. The project does not contain deployment credentials, CI/CD
triggers, production mutation code, or autonomous deployment actions.
