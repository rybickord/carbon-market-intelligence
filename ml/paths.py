"""Project-root path helpers. Never hardcode machine-specific absolute paths."""

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def processed_dir() -> Path:
    return project_root() / "data" / "processed"


def models_dir() -> Path:
    return project_root() / "ml" / "models"


def docs_dir() -> Path:
    return project_root() / "docs"
