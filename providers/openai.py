"""OpenAI provider for email classification."""

from openai import OpenAI

from providers.base import ClassificationResult, Provider


class OpenAIProvider(Provider):
    """OpenAI/ChatGPT provider."""

    @property
    def default_model(self) -> str:
        return "gpt-5-mini"

    @property
    def name(self) -> str:
        return "OpenAI"

    def classify(self, prompt: str) -> ClassificationResult:
        """Classify email using OpenAI API."""
        try:
            client = OpenAI(api_key=self.api_key)
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
