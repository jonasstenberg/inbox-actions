"""Mistral AI provider for email classification."""

from mistralai import Mistral

from providers.base import Provider


class MistralProvider(Provider):
    """Mistral AI provider."""

    @property
    def default_model(self) -> str:
        return "mistral-medium-latest"

    @property
    def name(self) -> str:
        return "Mistral"

    def _call_api(self, prompt: str) -> str:
        """Call Mistral API and return response content."""
        client = Mistral(api_key=self.api_key, timeout_ms=self.timeout * 1000)
        response = client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
