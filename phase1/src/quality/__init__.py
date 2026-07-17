"""Quality package."""

from .gates import QualityGates
from .language import attach_language, detect_language

__all__ = ["QualityGates", "attach_language", "detect_language"]
