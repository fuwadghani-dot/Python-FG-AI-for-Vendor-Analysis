"""UI helper utilities for the Streamlit app."""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
import time

DATA_SAMPLES = Path("data_samples")
REPORTS_DIR = Path("reports/exports")

DATA_SAMPLES.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(uploaded, prefix: str = "upload_") -> Path:
    """Save an uploaded file (Streamlit UploadedFile) to data_samples and return the Path."""
    name = uploaded.name if hasattr(uploaded, "name") else f"{int(time.time())}.xlsx"
    dest = DATA_SAMPLES / f"{prefix}{int(time.time())}_{name}"
    with dest.open("wb") as fh:
        fh.write(uploaded.getbuffer())
    return dest


def list_reports(limit: int = 10) -> List[Path]:
    """Return recent report files (sorted by modified time desc)."""
    files = [p for p in REPORTS_DIR.glob("*.xlsx") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def list_sample_workbooks() -> Iterable[Path]:
    """List available sample workbooks in DATA_SAMPLES."""
    return sorted(DATA_SAMPLES.glob("*.xlsx"))
