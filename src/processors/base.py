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

    def unprotect_text(self, text: str, *, role: str = "human-support-agent") -> str:
        """Restore original values from protected text.

        Only supported by processors that do reversible protection.
        Presidio's processor raises NotImplementedError here — that's
        the point.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not support unprotect."
        )
