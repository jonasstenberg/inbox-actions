"""Anthropic provider for email classification."""

import anthropic

from providers.base import ClassificationResult, Provider


class AnthropicProvider(Provider):
    """Anthropic/Claude provider."""

    @property
    def default_model(self) -> str:
        return "claude-haiku-4-5"

    @property
    def name(self) -> str:
        return "Anthropic"

    def classify(self, prompt: str) -> ClassificationResult:
        """Classify email using Anthropic API."""
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text.strip()
            return self.parse_response(content)
        except Exception as e:
            return ClassificationResult(
                needs_action=False,
                priority="low",
                reason=str(e)[:50],
            )
