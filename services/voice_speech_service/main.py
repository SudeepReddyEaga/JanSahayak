"""
FastAPI Microservice Entrypoint for Voice & Speech Service (Port 8004).
Exposes stateless endpoints for querying supported BCP-47 speech locales and
converting localized scheme guides into speech-optimized utterance segments.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.voice_speech_service.service import (
    SpeechTextSanitizerService,
    VoiceLocaleRegistryService,
)
from shared.domain.enums import LanguageCode
from shared.domain.models import PreparedSpeechPayload, PrepareSpeechRequest, VoiceLocaleSpec
from shared.infrastructure.logging_utils import get_logger

# Instantiate logger and singletons following Dependency Inversion
logger = get_logger("voice-speech-service")
locale_registry = VoiceLocaleRegistryService()
speech_sanitizer = SpeechTextSanitizerService(locale_registry=locale_registry)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup hook logging active BCP-47 speech locale count."""
    logger.info("Voice & Speech Microservice initialized with %d locales", len(locale_registry.list_locales()))
    yield


app = FastAPI(
    title="Multilingual Welfare Scheme Guide — Voice & Speech Service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, object]:
    """Liveness check reporting total registered voice locales."""
    locales = locale_registry.list_locales()
    return {
        "status": "ok",
        "service": "voice-speech-service",
        "supported_languages": len(locales),
    }


@app.get("/voice/locales", response_model=list[VoiceLocaleSpec])
def list_voice_locales() -> list[VoiceLocaleSpec]:
    """Return full list of 12 citizen language voice locale specifications."""
    return locale_registry.list_locales()


@app.get("/voice/locales/{language}", response_model=VoiceLocaleSpec)
def get_voice_locale(language: LanguageCode) -> VoiceLocaleSpec:
    """Resolve voice specification for a single ISO LanguageCode."""
    return locale_registry.get_locale(language)


@app.post("/voice/prepare-speech", response_model=PreparedSpeechPayload)
def prepare_speech_segments(request: PrepareSpeechRequest) -> PreparedSpeechPayload:
    """Sanitize Markdown welfare guidance into browser-safe speech utterance chunks."""
    return speech_sanitizer.prepare_speech(text=request.text, language=request.language)

