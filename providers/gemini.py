"""Google Gemini provider for email classification."""

from google import genai
from google.genai import types

from providers.base import Provider


class GeminiProvider(Provider):
    """Google Gemini provider."""

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    @property
    def name(self) -> str:
        return "Gemini"

    def _call_api(self, prompt: str) -> str:
        """Call Gemini API and return response content."""
        client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=self.timeout * 1000),
        )
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text.strip()
