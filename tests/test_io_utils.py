"""Tests for io_utils — reading and writing files."""

import json
from pathlib import Path

from src.io_utils import read_ticket, write_outputs
from src.models import Finding, ProcessResult


SAMPLE_TEXT = "Hello, my name is Sarah Johnson."


def _make_result(sanitized: str = "Hello, my name is <PERSON>.") -> ProcessResult:
    return ProcessResult(
        original_text=SAMPLE_TEXT,
        sanitized_text=sanitized,
        findings=[
            Finding(
                entity_type="PERSON",
                start=18,
                end=31,
                score=0.85,
                original_value="Sarah Johnson",
            )
        ],
        processor_name="test",
    )


def test_read_ticket(tmp_path: Path) -> None:
    ticket = tmp_path / "ticket.txt"
    ticket.write_text("test content", encoding="utf-8")
    assert read_ticket(ticket) == "test content"


def test_write_outputs_creates_files(tmp_path: Path) -> None:
    result = _make_result()
    sanitized_path, findings_path = write_outputs(result, tmp_path)

    assert sanitized_path.exists()
    assert findings_path.exists()
    assert sanitized_path.read_text(encoding="utf-8") == result.sanitized_text


def test_findings_json_is_valid(tmp_path: Path) -> None:
    result = _make_result()
    _, findings_path = write_outputs(result, tmp_path)

    data = json.loads(findings_path.read_text(encoding="utf-8"))
    assert data["processor"] == "test"
    assert data["total_findings"] == 1
    assert len(data["findings"]) == 1
