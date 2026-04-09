"""File I/O helpers for reading tickets and writing outputs."""

import json
from dataclasses import asdict
from pathlib import Path

from src.config import SANITIZED_FILENAME, FINDINGS_FILENAME
from src.models import ProcessResult


def read_ticket(path: str | Path) -> str:
    """Read and return the full text of a ticket file."""
    return Path(path).read_text(encoding="utf-8")


def write_outputs(result: ProcessResult, output_dir: str | Path) -> tuple[Path, Path]:
    """Write sanitized text and findings JSON to *output_dir*.

    Returns (sanitized_path, findings_path).
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    sanitized_path = out / SANITIZED_FILENAME
    sanitized_path.write_text(result.sanitized_text, encoding="utf-8")

    findings_path = out / FINDINGS_FILENAME
    findings_data = {
        "processor": result.processor_name,
        "total_findings": len(result.findings),
        "findings": [asdict(f) for f in result.findings],
        "notes": result.notes,
    }
    findings_path.write_text(
        json.dumps(findings_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return sanitized_path, findings_path
