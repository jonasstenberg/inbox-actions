"""Mistral AI provider for email classification."""

from mistralai import Mistral

from providers.base import ClassificationResult, Provider


class MistralProvider(Provider):
    """Mistral AI provider."""

    @property
    def default_model(self) -> str:
        return "mistral-medium-latest"

    @property
    def name(self) -> str:
        return "Mistral"

    def classify(self, prompt: str) -> ClassificationResult:
        """Classify email using Mistral API."""
        try:
            client = Mistral(api_key=self.api_key)
            response = client.chat.complete(
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
