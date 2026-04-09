"""Processor-agnostic application workflow.

This module does not know about Presidio internals.  It receives a
BaseProcessor instance, runs it, and delegates I/O and reporting.
When we later swap to a Protegrity processor this file stays unchanged.
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
