"""Ollama provider for local LLM inference."""

import os

from openai import OpenAI

from providers.base import Provider


class OllamaProvider(Provider):
    """Ollama provider for local LLMs."""

    def __init__(self, api_key: str = "ollama", model: str | None = None):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        super().__init__(api_key or "ollama", model)

    @property
    def default_model(self) -> str:
        return "llama3.2"

    @property
    def name(self) -> str:
        return "Ollama"

    def _call_api(self, prompt: str) -> str:
        """Call Ollama API and return response content."""
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
