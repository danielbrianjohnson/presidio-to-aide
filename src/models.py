"""Data models shared across all processors and reporters."""

from dataclasses import dataclass, field


@dataclass
class Finding:
    """A single PII entity detected in the text."""
    entity_type: str
    start: int
    end: int
    score: float
    original_value: str


@dataclass
class ProcessResult:
    """The result of running a processor over a piece of text.

    This is the contract between any processor implementation and the
    rest of the application.  Keep it stable — the future Protegrity
    processor will return this same type.
    """
    original_text: str
    sanitized_text: str
    findings: list[Finding]
    processor_name: str
    notes: list[str] = field(default_factory=list)
