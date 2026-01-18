"""Ollama provider for local LLM inference."""

import os

from openai import OpenAI

from providers.base import ClassificationResult, Provider


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

    def classify(self, prompt: str) -> ClassificationResult:
        """Classify email using local Ollama instance."""
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content.strip()
            return self.parse_response(content)
        except Exception:
            return ClassificationResult(
                needs_action=False,
                priority="low",
                reason="API error occurred",
            )
