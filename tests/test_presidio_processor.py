"""Tests for the Presidio processor."""

from src.models import ProcessResult
from src.processors.presidio_processor import PresidioProcessor


def _get_processor() -> PresidioProcessor:
    return PresidioProcessor()


def test_process_returns_process_result() -> None:
    processor = _get_processor()
    result = processor.process_text("My name is Sarah Johnson.")
    assert isinstance(result, ProcessResult)
    assert result.processor_name == "presidio"


def test_sanitized_text_differs_when_pii_found() -> None:
    processor = _get_processor()
    text = "Call me at 415-555-0199 or email sarah@example.com."
    result = processor.process_text(text)
    assert result.sanitized_text != result.original_text
    assert len(result.findings) > 0


def test_detects_email() -> None:
    processor = _get_processor()
    result = processor.process_text("Contact sarah.johnson@example.com please.")
    entity_types = {f.entity_type for f in result.findings}
    assert "EMAIL_ADDRESS" in entity_types


def test_detects_ssn() -> None:
    processor = _get_processor()
    result = processor.process_text("SSN: 539-48-2017")
    entity_types = {f.entity_type for f in result.findings}
    assert "US_SSN" in entity_types


def test_detects_phone() -> None:
    processor = _get_processor()
    result = processor.process_text("Phone: 415-555-0199")
    entity_types = {f.entity_type for f in result.findings}
    assert "PHONE_NUMBER" in entity_types


def test_no_findings_for_clean_text() -> None:
    processor = _get_processor()
    result = processor.process_text("The weather is nice today.")
    assert len(result.findings) == 0
    assert result.sanitized_text == result.original_text
