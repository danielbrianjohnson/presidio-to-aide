"""Presidio-based PII processor.

Uses Microsoft Presidio's AnalyzerEngine and AnonymizerEngine to detect
and redact PII.  Custom recognizers are added here — they are isolated
in helper methods so they can be removed when swapping to a different
processor backend.
"""

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from src.config import PRESIDIO_LANGUAGE, PRESIDIO_ENTITIES, ANON_PLACEHOLDER
from src.models import Finding, ProcessResult
from src.processors.base import BaseProcessor


class PresidioProcessor(BaseProcessor):
    """Detect and anonymize PII using Microsoft Presidio."""

    def __init__(self) -> None:
        self._analyzer = AnalyzerEngine()
        self._anonymizer = AnonymizerEngine()
        self._register_custom_recognizers()

    # ------------------------------------------------------------------
    # Custom recognizers
    # ------------------------------------------------------------------

    def _register_custom_recognizers(self) -> None:
        """Register lightweight custom recognizers for entities that
        Presidio's built-in models don't cover well.

        Each recognizer is built in its own helper so it's easy to
        remove or replace individually.
        """
        self._add_account_number_recognizer()

    def _add_account_number_recognizer(self) -> None:
        """Detect simple numeric account numbers (8+ digits)."""
        account_pattern = Pattern(
            name="account_number_pattern",
            regex=r"\b\d{8,12}\b",
            score=0.5,
        )
        recognizer = PatternRecognizer(
            supported_entity="ACCOUNT_NUMBER",
            patterns=[account_pattern],
            context=["account", "account number", "acct"],
        )
        self._analyzer.registry.add_recognizer(recognizer)

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------

    def process_text(self, text: str) -> ProcessResult:
        """Analyze and anonymize *text*, returning a ProcessResult."""
        entities_to_detect = PRESIDIO_ENTITIES + ["ACCOUNT_NUMBER"]

        analyzer_results = self._analyzer.analyze(
            text=text,
            language=PRESIDIO_LANGUAGE,
            entities=entities_to_detect,
        )

        # Build operator map so each entity type gets a readable placeholder
        operators = {
            result.entity_type: OperatorConfig(
                "replace",
                {"new_value": ANON_PLACEHOLDER.format(entity_type=result.entity_type)},
            )
            for result in analyzer_results
        }

        anonymized = self._anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=operators,
        )

        findings = [
            Finding(
                entity_type=r.entity_type,
                start=r.start,
                end=r.end,
                score=round(r.score, 2),
                original_value=text[r.start : r.end],
            )
            for r in analyzer_results
        ]

        notes: list[str] = []
        if not findings:
            notes.append("No PII entities detected.")

        return ProcessResult(
            original_text=text,
            sanitized_text=anonymized.text,
            findings=findings,
            processor_name="presidio",
            notes=notes,
        )
