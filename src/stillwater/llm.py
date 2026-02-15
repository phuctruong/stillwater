"""LLM client for Stillwater OS.

Single interface supporting Ollama and OpenAI-compatible APIs.
"""

from __future__ import annotations

import requests

from stillwater.config import StillwaterConfig, load_config


class LLMError(Exception):
    """Raised when LLM generation fails."""


class LLMClient:
    """Synchronous LLM client supporting Ollama and OpenAI APIs."""

    def __init__(
        self,
        config: StillwaterConfig | None = None,
        *,
        model: str | None = None,
        provider: str | None = None,
    ) -> None:
        self._config = config or load_config()
        if provider:
            self._config.llm.provider = provider
        if model:
            if self._config.llm.provider == "ollama":
                self._config.llm.ollama.model = model
            else:
                self._config.llm.openai.model = model

    @property
    def provider(self) -> str:
        return self._config.llm.provider

    @property
    def model(self) -> str:
        if self.provider == "ollama":
            return self._config.llm.ollama.model
        return self._config.llm.openai.model

    @property
    def endpoint(self) -> str:
        if self.provider == "ollama":
            return self._config.llm.ollama.base_url
        return self._config.llm.openai.base_url

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        timeout: float = 120.0,
    ) -> str:
        """Generate a completion from the LLM.

        Args:
            prompt: The input prompt.
            temperature: Override temperature (use 0 for determinism).
            timeout: Request timeout in seconds.

        Returns:
            The generated text.

        Raises:
            LLMError: On any generation failure.
        """
        if self.provider == "ollama":
            return self._generate_ollama(prompt, temperature, timeout)
        elif self.provider == "openai":
            return self._generate_openai(prompt, temperature, timeout)
        else:
            raise LLMError(f"unknown provider: {self.provider}")

    def _generate_ollama(
        self, prompt: str, temperature: float | None, timeout: float
    ) -> str:
        url = f"{self._config.llm.ollama.base_url}/api/generate"
        payload: dict = {
            "model": self._config.llm.ollama.model,
            "prompt": prompt,
            "stream": False,
        }
        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json()["response"].strip()
        except requests.RequestException as e:
            raise LLMError(f"Ollama request failed: {e}") from e
        except (KeyError, ValueError) as e:
            raise LLMError(f"Ollama response parse failed: {e}") from e

    def _generate_openai(
        self, prompt: str, temperature: float | None, timeout: float
    ) -> str:
        url = f"{self._config.llm.openai.base_url}/chat/completions"
        headers: dict = {"Content-Type": "application/json"}
        if self._config.llm.openai.api_key:
            headers["Authorization"] = f"Bearer {self._config.llm.openai.api_key}"

        payload: dict = {
            "model": self._config.llm.openai.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature is not None:
            payload["temperature"] = temperature

        try:
            resp = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except requests.RequestException as e:
            raise LLMError(f"OpenAI request failed: {e}") from e
        except (KeyError, IndexError, ValueError) as e:
            raise LLMError(f"OpenAI response parse failed: {e}") from e
