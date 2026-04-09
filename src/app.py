"""Processor-agnostic application workflow.

This module does not know about Presidio or Protegrity internals.
It receives a BaseProcessor instance and orchestrates the workflow.
"""

from pathlib import Path

from src.processors.base import BaseProcessor
from src.io_utils import read_ticket, write_outputs
from src.reporters.console_reporter import print_console_report


def run(processor: BaseProcessor, input_path: str, output_dir: str) -> None:
    """End-to-end: read ticket → process → write outputs → report."""
    text = read_ticket(input_path)
    result = processor.process_text(text)
    sanitized_path, findings_path = write_outputs(result, output_dir)
    print_console_report(result, sanitized_path, findings_path)


def run_unprotect(processor: BaseProcessor, input_path: str, output_dir: str, role: str) -> None:
    """Read a protected ticket and restore original values."""
    protected_text = read_ticket(input_path)

    try:
        restored_text = processor.unprotect_text(protected_text, role=role)
    except PermissionError as exc:
        print("\n" + "=" * 50)
        print("  ACCESS DENIED")
        print("=" * 50)
        print(f"  {exc}")
        print("=" * 50)
        return

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    restored_path = out / "restored_ticket.txt"
    restored_path.write_text(restored_text, encoding="utf-8")

    print("\n" + "=" * 50)
    print("  Ticket Unprotection Report")
    print("=" * 50)
    print(f"  Processor : {processor.__class__.__name__}")
    print(f"  Restored  → {restored_path}")
    print("=" * 50)
    print("\n--- Restored Text ---")
    print(restored_text)
