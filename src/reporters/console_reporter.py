"""Print a short human-readable summary to the console."""

from collections import Counter
from pathlib import Path

from src.models import ProcessResult


def print_console_report(
    result: ProcessResult,
    sanitized_path: Path,
    findings_path: Path,
) -> None:
    """Print a concise summary of the sanitization run."""
    entity_counts = Counter(f.entity_type for f in result.findings)

    print("\n" + "=" * 50)
    print("  Ticket Sanitization Report")
    print("=" * 50)
    print(f"  Processor : {result.processor_name}")
    print(f"  Findings  : {len(result.findings)}")

    if entity_counts:
        print("  Entities  :")
        for entity, count in sorted(entity_counts.items()):
            print(f"    - {entity}: {count}")

    if result.notes:
        print("  Notes     :")
        for note in result.notes:
            print(f"    - {note}")

    print(f"\n  Sanitized → {sanitized_path}")
    print(f"  Report    → {findings_path}")
    print("=" * 50)

    print("\n--- Sanitized Text ---")
    print(result.sanitized_text)
