"""Dataset loading, persistence, and hashing."""

from __future__ import annotations

import hashlib
import os
import warnings
from datetime import datetime

import pandas as pd

from config import DATASET_PATH, SHEET_NAME

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def dataset_exists() -> bool:
    """Return True if dataset.xlsx is present at the project root."""
    return os.path.isfile(DATASET_PATH)


def load_dataset(path: str = DATASET_PATH) -> pd.DataFrame:
    """Load the dataset from the given path. Raises FileNotFoundError if missing."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Dataset not found at {path}")
    return pd.read_excel(path, sheet_name=SHEET_NAME)


def save_uploaded_dataset(file_bytes: bytes, path: str = DATASET_PATH) -> None:
    """Persist uploaded bytes to *path* (overwriting if needed)."""
    with open(path, "wb") as f:
        f.write(file_bytes)


def dataset_hash(path: str = DATASET_PATH) -> str:
    """SHA-256 of the dataset file (first 12 chars). Empty string if missing."""
    if not os.path.isfile(path):
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def dataset_modified(path: str = DATASET_PATH) -> str:
    """Human-readable last-modified timestamp, or 'N/A' if missing."""
    if not os.path.isfile(path):
        return "N/A"
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def dataset_filename(path: str = DATASET_PATH) -> str:
    """Just the basename of the dataset file."""
    return os.path.basename(path)
