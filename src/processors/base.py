"""Abstract base class for PII processors.

This is the main migration seam.  Any new processor (e.g. Protegrity)
should subclass BaseProcessor and implement process_text().
"""

from abc import ABC, abstractmethod
from src.models import ProcessResult


class BaseProcessor(ABC):
    """Interface that every PII processor must satisfy."""

    @abstractmethod
    def process_text(self, text: str) -> ProcessResult:
        """Detect and sanitize PII in *text*, returning a ProcessResult."""
        ...
