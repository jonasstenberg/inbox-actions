"""AI providers for email classification."""

from providers.base import ClassificationResult, Provider
from providers.mistral import MistralProvider
from providers.openai import OpenAIProvider
from providers.anthropic import AnthropicProvider
from providers.gemini import GeminiProvider
from providers.ollama import OllamaProvider
from providers.mock import MockProvider

# Registry of available providers
PROVIDERS: dict[str, type[Provider]] = {
    "mistral": MistralProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "mock": MockProvider,
}

# Environment variable names for each provider's API key
# Mock and Ollama providers have no key requirement
PROVIDER_API_KEYS: dict[str, str] = {
    "mistral": "MISTRAL_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

DEFAULT_PROVIDER = "ollama"

__all__ = [
    "Provider",
    "ClassificationResult",
    "MistralProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "OllamaProvider",
    "MockProvider",
    "PROVIDERS",
    "PROVIDER_API_KEYS",
    "DEFAULT_PROVIDER",
]
