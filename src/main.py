"""CLI entry point for the ticket sanitizer.

Usage:
    python -m src.main protect --input ticket.txt --output-dir output
    python -m src.main unprotect --role human-support-agent --input output/sanitized_ticket.txt --output-dir output/recovered
"""

import argparse

from dotenv import load_dotenv
load_dotenv()

from src.config import DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_DIR
from src.processors.protegrity_processor import ProtegrityProcessor
from src.app import run, run_unprotect


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Protect or unprotect PII in a support ticket."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- protect --
    protect_parser = subparsers.add_parser(
        "protect", help="Detect and tokenize PII in a ticket."
    )
    protect_parser.add_argument(
        "--input",
        default=DEFAULT_INPUT_FILE,
        help=f"Path to the input ticket file (default: {DEFAULT_INPUT_FILE})",
    )
    protect_parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for output files (default: {DEFAULT_OUTPUT_DIR})",
    )

    # -- unprotect --
    unprotect_parser = subparsers.add_parser(
        "unprotect", help="Restore original values from a protected ticket."
    )
    unprotect_parser.add_argument(
        "--role",
        required=True,
        choices=["human-support-agent", "ai-support-agent"],
        help="Role requesting access (human-support-agent=authorized, ai-support-agent=denied).",
    )
    unprotect_parser.add_argument(
        "--input",
        required=True,
        help="Path to the protected ticket file.",
    )
    unprotect_parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for output files (default: {DEFAULT_OUTPUT_DIR})",
    )

    args = parser.parse_args()
    processor = ProtegrityProcessor()

    if args.command == "protect":
        run(processor, args.input, args.output_dir)
    elif args.command == "unprotect":
        run_unprotect(processor, args.input, args.output_dir, args.role)


if __name__ == "__main__":
    main()
