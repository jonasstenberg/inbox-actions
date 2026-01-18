"""OpenAI provider for email classification."""

from openai import OpenAI

from providers.base import Provider


class OpenAIProvider(Provider):
    """OpenAI/ChatGPT provider."""

    @property
    def default_model(self) -> str:
        return "gpt-5-mini"

    @property
    def name(self) -> str:
        return "OpenAI"

    def _call_api(self, prompt: str) -> str:
        """Call OpenAI API and return response content."""
        client = OpenAI(api_key=self.api_key, timeout=self.timeout)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
