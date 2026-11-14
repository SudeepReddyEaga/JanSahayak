"""
Voice & Speech Interface Contracts (Interface Segregation & Dependency Inversion).
Defines clean LLD abstractions separating BCP-47 voice locale metadata and
speech-safe text sanitization from HTTP microservice handlers and browser TTS/STT.
"""

from abc import ABC, abstractmethod

from shared.domain.enums import LanguageCode
from shared.domain.models import PreparedSpeechPayload, VoiceLocaleSpec


class IVoiceLocaleRegistry(ABC):
    """Contract for resolving speech recognition (STT) and synthesis (TTS) locale specs."""

    @abstractmethod
    def list_locales(self) -> list[VoiceLocaleSpec]:
        """Return voice configuration metadata for every supported citizen language."""

    @abstractmethod
    def get_locale(self, language: LanguageCode) -> VoiceLocaleSpec:
        """Resolve exact BCP-47 speech locale specification for a target LanguageCode."""


class ISpeechTextSanitizer(ABC):
    """Contract for converting formatted Markdown guides into clean spoken audio segments."""

    @abstractmethod
    def prepare_speech(self, *, text: str, language: LanguageCode) -> PreparedSpeechPayload:
        """Sanitize Markdown/URLs while keeping official scheme names clearly pronounceable."""

