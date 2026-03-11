"""
LLM Manager — LangChain-based unified LLM client for text generation with streaming.

Supports:
- OpenAI-compatible APIs (yunwu.ai proxy)
- Per-call temperature override
- Streaming via async generator
- Multimodal messages (text + image_url)

NOT used for image generation (that stays in GeminiClient with httpx).

Provider-agnostic initialization example (for future use):
    # from langchain.chat_models import init_chat_model
    # model = init_chat_model("openai:gpt-4o", base_url=..., api_key=...)
    # model = init_chat_model("anthropic:claude-sonnet-4-6")
"""

from typing import AsyncGenerator, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from config import Settings


class LLMManager:
    """Unified LLM manager using LangChain ChatOpenAI for text generation."""

    def __init__(self, settings: Settings):
        self.settings = settings
        api_key = settings.gemini_analyze_api_key.get_secret_value()
        self.model = ChatOpenAI(
            base_url=settings.analyze_openai_base_url,
            api_key=api_key,  # type: ignore[arg-type]
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            streaming=True,
            timeout=settings.llm_timeout,
        )

    def _make_model(self, temperature: float) -> ChatOpenAI:
        """Create a ChatOpenAI instance with the given temperature."""
        api_key = self.settings.gemini_analyze_api_key.get_secret_value()
        return ChatOpenAI(
            base_url=self.settings.analyze_openai_base_url,
            api_key=api_key,  # type: ignore[arg-type]
            model=self.settings.llm_model,
            temperature=temperature,
            streaming=True,
            timeout=self.settings.llm_timeout,
        )

    def _convert_messages(self, messages: list[dict]) -> list[BaseMessage]:
        """
        Convert OpenAI-style message dicts to LangChain message objects.

        Supports:
        - {"role": "system", "content": "..."}
        - {"role": "user", "content": "plain text"}
        - {"role": "user", "content": [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {"url": "..."}}]}
        """
        lc_messages: list[BaseMessage] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                lc_messages.append(SystemMessage(content=str(content)))
            elif role == "user":
                if isinstance(content, str):
                    lc_messages.append(HumanMessage(content=content))
                elif isinstance(content, list):
                    # Multimodal: list of content blocks (text + image_url)
                    lc_content = []
                    for block in content:
                        block_type = block.get("type", "text")
                        if block_type == "text":
                            lc_content.append({"type": "text", "text": block.get("text", "")})
                        elif block_type == "image_url":
                            lc_content.append({
                                "type": "image_url",
                                "image_url": block.get("image_url", {})
                            })
                    lc_messages.append(HumanMessage(content=lc_content))  # type: ignore[arg-type]
                else:
                    lc_messages.append(HumanMessage(content=str(content)))

        return lc_messages

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat response as text chunks.

        Args:
            messages: List of OpenAI-style message dicts
            temperature: Optional per-call temperature override

        Yields:
            Text chunks as they arrive from the model
        """
        lc_messages = self._convert_messages(messages)

        # Apply per-call temperature override if provided
        if temperature is not None and temperature != self.settings.llm_temperature:
            model = self._make_model(temperature)
        else:
            model = self.model

        try:
            async for chunk in model.astream(lc_messages):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    if isinstance(content, str):
                        yield content
        except Exception as e:
            raise RuntimeError(f"LLM streaming error: {str(e)}") from e

    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None
    ) -> str:
        """
        Non-streaming chat — returns full response as a string.

        Args:
            messages: List of OpenAI-style message dicts
            temperature: Optional per-call temperature override

        Returns:
            Full response text
        """
        lc_messages = self._convert_messages(messages)

        if temperature is not None and temperature != self.settings.llm_temperature:
            model = self._make_model(temperature)
        else:
            model = self.model

        try:
            response = await model.ainvoke(lc_messages)
            content = response.content
            return str(content) if not isinstance(content, str) else content
        except Exception as e:
            raise RuntimeError(f"LLM chat error: {str(e)}") from e
