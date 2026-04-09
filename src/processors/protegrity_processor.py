"""Protegrity Developer Edition PII processor.

Uses the protegrity_developer_python module to detect and protect PII.
Presidio still runs inside Dev Edition's Data Discovery service —
we just call it through the unified API instead of managing it directly.

The key difference from PresidioProcessor:
  - Detection and protection happen in a single find_and_protect() call
  - Protection is reversible via find_and_unprotect()
  - No need to manage AnalyzerEngine, AnonymizerEngine, or custom recognizers
"""

import re

import protegrity_developer_python as protegrity

from src.config import PROTEGRITY_ENDPOINT_URL, PROTEGRITY_ENTITY_MAP, PROTEGRITY_SCORE_THRESHOLD
from src.models import Finding, ProcessResult
from src.processors.base import BaseProcessor


class ProtegrityProcessor(BaseProcessor):
    """Detect and protect PII using Protegrity Developer Edition."""

    def __init__(self) -> None:
        protegrity.configure(
            endpoint_url=PROTEGRITY_ENDPOINT_URL,
            named_entity_map=PROTEGRITY_ENTITY_MAP,
            classification_score_threshold=PROTEGRITY_SCORE_THRESHOLD,
        )

    def process_text(self, text: str) -> ProcessResult:
        """Detect and tokenize PII in *text* via find_and_protect()."""
        protected_text = protegrity.find_and_protect(text)
        findings = self._extract_findings(protected_text)

        notes: list[str] = []
        if not findings:
            notes.append("No PII entities detected.")

        return ProcessResult(
            original_text=text,
            sanitized_text=protected_text,
            findings=findings,
            processor_name="protegrity",
            notes=notes,
        )

    _AUTHORIZED_ROLES = {"human-support-agent"}

    def unprotect_text(self, text: str, *, role: str = "human-support-agent") -> str:
        """Restore original values from a previously protected text.

        In a production Protegrity deployment the policy engine enforces
        role-based access.  Here we simulate the same gate.
        """
        if role not in self._AUTHORIZED_ROLES:
            raise PermissionError(
                f"Access denied: role '{role}' is not authorized to unprotect data.\n"
                "In production, Protegrity's policy engine controls which roles "
                "can reverse tokenization."
            )
        return protegrity.find_and_unprotect(text)

    @staticmethod
    def _extract_findings(protected_text: str) -> list[Finding]:
        """Parse entity tags like [PERSON]token[/PERSON] from protected output."""
        pattern = re.compile(r"\[([A-Z_]+)\](.*?)\[/\1\]")
        findings: list[Finding] = []
        for match in pattern.finditer(protected_text):
            findings.append(
                Finding(
                    entity_type=match.group(1),
                    start=match.start(),
                    end=match.end(),
                    score=1.0,
                    original_value=match.group(2),
                )
            )
        return findings
