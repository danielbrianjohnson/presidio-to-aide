"""End-to-end test for the app workflow."""

from pathlib import Path

from src.app import run
from src.processors.presidio_processor import PresidioProcessor


def test_app_end_to_end(tmp_path: Path) -> None:
    # Write a small test ticket
    ticket = tmp_path / "ticket.txt"
    ticket.write_text(
        "Customer: Sarah Johnson\n"
        "Email: sarah.johnson@example.com\n"
        "SSN: 539-48-2017\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "output"
    processor = PresidioProcessor()
    run(processor, str(ticket), str(output_dir))

    sanitized = output_dir / "sanitized_ticket.txt"
    findings = output_dir / "findings.json"

    assert sanitized.exists()
    assert findings.exists()

    sanitized_text = sanitized.read_text(encoding="utf-8")
    assert "Sarah Johnson" not in sanitized_text
    assert "539-48-2017" not in sanitized_text
