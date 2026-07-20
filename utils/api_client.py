"""
Thin wrapper around an OpenAI-compatible chat completions API.

Works with any server that implements the OpenAI `/v1/chat/completions`
and `/v1/models` endpoints (FreeLLMAPI, Ollama's OpenAI-compat mode,
LM Studio, vLLM, llama.cpp server, actual OpenAI, etc). No model names
are hardcoded anywhere in this module.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from openai import APIConnectionError, APIStatusError, OpenAI, OpenAIError

from config.config_manager import AppConfig


class APIClientError(Exception):
    """Raised for any failure talking to the LLM backend."""


@dataclass
class ModelInfo:
    id: str
    owned_by: str = "unknown"
    context_length: int | None = None
    status: str = "available"


class LLMClient:
    """Wraps the OpenAI SDK so the rest of the app never touches it directly."""

    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self._client = OpenAI(
            api_key=cfg.api_key or "not-needed",
            base_url=cfg.base_url,
        )

    def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Generator[str, None, None]:
        """Yield response text chunks as they arrive from the server."""
        try:
            stream = self._client.chat.completions.create(
                model=model or self.cfg.default_model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature if temperature is not None else self.cfg.temperature,
                max_tokens=max_tokens or self.cfg.max_tokens,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    yield content
        except (APIConnectionError, APIStatusError, OpenAIError) as exc:
            raise APIClientError(self._friendly_error(exc)) from exc

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Non-streaming call; returns the full response text at once."""
        try:
            response = self._client.chat.completions.create(
                model=model or self.cfg.default_model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature if temperature is not None else self.cfg.temperature,
                max_tokens=max_tokens or self.cfg.max_tokens,
                stream=False,
            )
            return response.choices[0].message.content or ""
        except (APIConnectionError, APIStatusError, OpenAIError) as exc:
            raise APIClientError(self._friendly_error(exc)) from exc

    def list_models(self) -> list[ModelInfo]:
        try:
            response = self._client.models.list()
        except (APIConnectionError, APIStatusError, OpenAIError) as exc:
            raise APIClientError(self._friendly_error(exc)) from exc

        models: list[ModelInfo] = []
        for m in response.data:
            owned_by = getattr(m, "owned_by", "unknown") or "unknown"
            context_length = (
                getattr(m, "context_length", None)
                or getattr(m, "context_window", None)
            )
            models.append(ModelInfo(id=m.id, owned_by=owned_by, context_length=context_length))
        return models

    def _friendly_error(self, exc: Exception) -> str:
        if isinstance(exc, APIConnectionError):
            return (
                f"Could not reach the API at {self.cfg.base_url}. "
                "Is FreeLLMAPI (or your backend) running? "
                "Check the base URL with `ai config`."
            )
        if isinstance(exc, APIStatusError):
            status = getattr(exc, "status_code", "unknown")
            return f"API returned an error (status {status}): {exc}"
        return f"Unexpected API error: {exc}"
