"""Build a JSON-serialisable dict from a ProcessResult."""

from dataclasses import asdict

from src.models import ProcessResult


def build_findings_dict(result: ProcessResult) -> dict:
    """Return a plain dict suitable for JSON serialization."""
    return {
        "processor": result.processor_name,
        "total_findings": len(result.findings),
        "findings": [asdict(f) for f in result.findings],
        "notes": result.notes,
    }
