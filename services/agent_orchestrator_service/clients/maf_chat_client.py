"""
Microsoft Agent Framework ChatClient Implementations & Factory (Factory + Strategy Patterns).
Implements DeterministicMultilingualChatClient extending MAF's FunctionInvocationLayer +
BaseChatClient so the multi-agent pipeline runs cleanly out-of-the-box with zero external API keys,
while seamlessly supporting OpenAI, Gemini, or Ollama MAF clients when credentials are provided.
"""

from collections.abc import AsyncIterable, Mapping, Sequence
from typing import Any
import uuid

from agent_framework import (
    BaseChatClient,
    ChatResponse,
    ChatResponseUpdate,
    FunctionInvocationLayer,
    Message,
    SupportsChatGetResponse,
)

from shared.config.settings import AppSettings
from shared.infrastructure.logging_utils import get_logger

logger = get_logger("maf-chat-client")


class DeterministicMultilingualChatClient(FunctionInvocationLayer, BaseChatClient):
    """
    Offline, deterministic Microsoft Agent Framework ChatClient.
    Supports tool/function invocation and streaming updates inside Agent.run(),
    returning grounded role summaries derived strictly from injected ContextProvider memory.
    """

    OTEL_PROVIDER_NAME = "deterministic-multilingual-local"

    def __init__(self) -> None:
        super().__init__()

    async def _inner_get_response(
        self,
        *,
        messages: Sequence[Message],
        stream: bool,
        options: Mapping[str, Any],
        **kwargs: Any,
    ):
        """
        Validate MAF ChatOptions and synthesize a grounded assistant message summarizing
        the active pipeline step context passed by the agent and ContextProvider.
        """
        await self._validate_options(options)
        # Extract the latest user/system instruction prompt text for deterministic grounding
        latest_text = messages[-1].text if messages else ""
        response_text = f"[MAF-Grounded-Agent] Processed context ({len(messages)} msgs): {latest_text[:280]}"
        response_id = f"det-{uuid.uuid4().hex[:12]}"

        if stream:
            async def _stream() -> AsyncIterable[ChatResponseUpdate]:
                yield ChatResponseUpdate(
                    role="assistant",
                    contents=[{"type": "text", "text": response_text}],
                    response_id=response_id,
                )

            return self._build_response_stream(_stream())

        return ChatResponse(
            messages=[Message(role="assistant", contents=[response_text])],
            response_id=response_id,
        )


class ChatClientFactory:
    """
    Factory creating the configured Microsoft Agent Framework chat client.
    Falls back gracefully to DeterministicMultilingualChatClient if optional cloud keys
    are absent or provider initialization fails.
    """

    @staticmethod
    def create_client(settings: AppSettings) -> SupportsChatGetResponse[Any]:
        """Instantiate MAF ChatClient according to AppSettings.llm_provider."""
        provider = (settings.llm_provider or "deterministic").lower().strip()

        if provider == "openai" and settings.openai_api_key:
            try:
                from agent_framework.openai import OpenAIChatClient

                logger.info(f"Using Microsoft Agent Framework OpenAIChatClient ({settings.openai_model})")
                return OpenAIChatClient(
                    model_id=settings.openai_model,
                    api_key=settings.openai_api_key,
                )
            except Exception as exc:
                logger.warning(f"OpenAIChatClient init failed ({exc}); using deterministic client.")

        if provider == "gemini" and settings.gemini_api_key:
            try:
                from agent_framework.gemini import GeminiChatClient

                logger.info(f"Using Microsoft Agent Framework GeminiChatClient ({settings.gemini_model})")
                return GeminiChatClient(
                    model_id=settings.gemini_model,
                    api_key=settings.gemini_api_key,
                )
            except Exception as exc:
                logger.warning(f"GeminiChatClient init failed ({exc}); using deterministic client.")

        if provider == "ollama":
            try:
                from agent_framework.ollama import OllamaChatClient

                logger.info(f"Using Microsoft Agent Framework OllamaChatClient ({settings.ollama_model})")
                return OllamaChatClient(
                    model_id=settings.ollama_model,
                    host=settings.ollama_host,
                )
            except Exception as exc:
                logger.warning(f"OllamaChatClient init failed ({exc}); using deterministic client.")

        return DeterministicMultilingualChatClient()

