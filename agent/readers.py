from pathlib import Path
from typing import Any
import json

import pandas as pd
from pypdf import PdfReader
from docx import Document


def read_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)


def read_json(file_path: str) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def read_docx(file_path: str) -> str:
    document = Document(file_path)
    return "\n".join(p.text for p in document.paragraphs)


def read_criteria(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return read_pdf(file_path)
    if suffix == ".docx":
        return read_docx(file_path)
    return Path(file_path).read_text(encoding="utf-8")
