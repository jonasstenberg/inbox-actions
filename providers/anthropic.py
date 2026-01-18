"""Anthropic provider for email classification."""

import anthropic

from providers.base import Provider


class AnthropicProvider(Provider):
    """Anthropic/Claude provider."""

    @property
    def default_model(self) -> str:
        return "claude-haiku-4-5"

    @property
    def name(self) -> str:
        return "Anthropic"

    def _call_api(self, prompt: str) -> str:
        """Call Anthropic API and return response content."""
        client = anthropic.Anthropic(api_key=self.api_key, timeout=self.timeout)
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
