"""
llm.py — the LLM service wrapper.
"""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, field

import config


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------
class LLMError(Exception):
    """Base class for all errors raised by the service."""
    user_message = "Something went wrong contacting the AI service."


class ConfigurationError(LLMError):
    """Terminal — missing/invalid key or bad setup."""
    user_message = "Error: API key is not configured.\nPlease check your .env file."


class InvalidRequestError(LLMError):
    """Terminal — request itself is malformed."""
    user_message = "The request could not be processed. Please adjust your input."


class RateLimitError(LLMError):
    """Transient — service is busy."""
    user_message = "The AI service is temporarily busy.\nPlease wait and try again."


class ServiceUnavailableError(LLMError):
    """Transient — network error, timeout, or temporary server fault."""
    user_message = "Unable to contact the AI service.\nPlease try again later."


# --------------------------------------------------------------------------
# Token usage
# --------------------------------------------------------------------------
@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens,
        )

    def format(self) -> str:
        return (
            f"[Usage: {self.input_tokens} input + {self.output_tokens} output "
            f"= {self.total_tokens} tokens]"
        )


@dataclass
class LLMService:
    """Resilient wrapper around Chat Completions API."""

    model: str = config.DEFAULT_MODEL
    temperature: float = config.DEFAULT_TEMPERATURE
    max_tokens: int = config.DEFAULT_MAX_TOKENS
    max_retries: int = config.MAX_RETRIES

    last_usage: Usage = field(default_factory=Usage)
    total_usage: Usage = field(default_factory=Usage)
    _client: object = field(default=None, repr=False)

    def _get_client(self):
        if self._client is not None:
            return self._client

        if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("GROQ_API_KEY"):
            raise ConfigurationError()

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ConfigurationError(
                "The 'openai' package is not installed. Run: pip install openai"
            ) from exc

        self._client = OpenAI()
        return self._client

    def ask(self, messages: list[dict], *, temperature=None, max_tokens=None) -> str:
        response = self._call_with_retries(
            messages,
            temperature=self._pick(temperature, self.temperature),
            max_tokens=self._pick(max_tokens, self.max_tokens),
            stream=False,
        )
        self._record_usage(response)
        return self._extract_text(response)

    def stream(self, messages: list[dict], *, temperature=None, max_tokens=None):
        stream = self._call_with_retries(
            messages,
            temperature=self._pick(temperature, self.temperature),
            max_tokens=self._pick(max_tokens, self.max_tokens),
            stream=True,
        )
        for chunk in stream:
            try:
                delta = chunk.choices[0].delta
                piece = getattr(delta, "content", None)
            except (AttributeError, IndexError):
                piece = None
            if piece:
                yield piece

    def _call_with_retries(self, messages, *, temperature, max_tokens, stream):
        attempt = 0
        while True:
            try:
                client = self._get_client()
                return client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                )
            except LLMError as err:
                if isinstance(err, (ConfigurationError, InvalidRequestError)):
                    raise
                self._sleep_or_raise(err, attempt)
                attempt += 1
            except Exception as raw:
                err = self._classify_error(raw)
                if isinstance(err, (ConfigurationError, InvalidRequestError)):
                    raise err
                self._sleep_or_raise(err, attempt)
                attempt += 1

    def _sleep_or_raise(self, err: LLMError, attempt: int):
        if attempt >= self.max_retries - 1:
            raise err
        delay = min(config.BACKOFF_BASE * (2 ** attempt), config.BACKOFF_MAX)
        delay += random.uniform(0, config.BACKOFF_BASE)
        time.sleep(delay)

    @staticmethod
    def _classify_error(raw: Exception) -> LLMError:
        name = type(raw).__name__.lower()
        text = str(raw).lower()

        if "authentication" in name or "permission" in name or "invalid api key" in text:
            return ConfigurationError()
        if "ratelimit" in name or "rate limit" in text or "429" in text:
            return RateLimitError()
        if "badrequest" in name or "invalidrequest" in name or "context length" in text:
            return InvalidRequestError()
        if any(k in name for k in ("timeout", "connection", "apierror", "internalserver")):
            return ServiceUnavailableError()
        return ServiceUnavailableError()

    def _record_usage(self, response) -> None:
        usage = getattr(response, "usage", None)
        inp = _first_attr(usage, ("prompt_tokens", "input_tokens"))
        out = _first_attr(usage, ("completion_tokens", "output_tokens"))
        self.last_usage = Usage(inp, out)
        self.total_usage = self.total_usage + self.last_usage

    @staticmethod
    def _extract_text(response) -> str:
        try:
            return response.choices[0].message.content or ""
        except (AttributeError, IndexError):
            return ""

    @staticmethod
    def _pick(value, default):
        return default if value is None else value


def _first_attr(obj, names, default=0):
    for n in names:
        val = getattr(obj, n, None)
        if val is not None:
            return int(val)
    return default
