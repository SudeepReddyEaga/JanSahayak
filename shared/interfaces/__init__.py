"""Abstract LLD Interface Contracts enforcing Dependency Inversion & Interface Segregation."""

from shared.interfaces.agent_interface import (
    IGroundingVerifier,
    ILanguageConsistencyReviewer,
    ISpecializedAgent,
)
from shared.interfaces.cache_interface import ICacheStore, ISemanticQueryCache
from shared.interfaces.repository_interface import (
    IEvaluationRepository,
    IProfileMemoryRepository,
    ISchemeRepository,
)
from shared.interfaces.retrieval_interface import IEmbeddingProvider, IVectorRetriever
from shared.interfaces.voice_interface import ISpeechTextSanitizer, IVoiceLocaleRegistry

__all__ = [
    "ICacheStore",
    "IEmbeddingProvider",
    "IEvaluationRepository",
    "IGroundingVerifier",
    "ILanguageConsistencyReviewer",
    "IProfileMemoryRepository",
    "ISchemeRepository",
    "ISemanticQueryCache",
    "ISpecializedAgent",
    "ISpeechTextSanitizer",
    "IVectorRetriever",
    "IVoiceLocaleRegistry",
]

