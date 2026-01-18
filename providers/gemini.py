"""Google Gemini provider for email classification."""

from google import genai

from providers.base import ClassificationResult, Provider


class GeminiProvider(Provider):
    """Google Gemini provider."""

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    @property
    def name(self) -> str:
        return "Gemini"

    def classify(self, prompt: str) -> ClassificationResult:
        """Classify email using Gemini API."""
        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            content = response.text.strip()
            return self.parse_response(content)
        except Exception as e:
            return ClassificationResult(
                needs_action=False,
                priority="low",
                reason=str(e)[:50],
            )
