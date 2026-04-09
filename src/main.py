"""CLI entry point for the ticket sanitizer.

Usage:
    python -m src.main --input ticket.txt --output-dir output
"""

import argparse

from src.config import DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_DIR
from src.processors.protegrity_processor import ProtegrityProcessor
from src.app import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sanitize PII in a support ticket."
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT_FILE,
        help=f"Path to the input ticket file (default: {DEFAULT_INPUT_FILE})",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for output files (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    processor = ProtegrityProcessor()

    run(processor, args.input, args.output_dir)


if __name__ == "__main__":
    main()
