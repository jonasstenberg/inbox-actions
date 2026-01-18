"""Email classification using AI providers."""

import os
import re
import sys
import time

from providers import PROVIDERS, PROVIDER_API_KEYS, DEFAULT_PROVIDER, Provider


def _sanitize_email_content(text: str, max_length: int = 1500) -> str:
    """Sanitize email content to mitigate prompt injection attacks.

    Wraps content in clear delimiters and truncates to max length.
    """
    if not text:
        return ""
    # Truncate to max length
    text = text[:max_length]
    # Replace sequences that might confuse the model about instruction boundaries
    text = re.sub(r"```+", "'''", text)
    return text


def load_prompt():
    """Load prompt template from prompt.md file."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: prompt.md not found at {prompt_path}")
        sys.exit(1)


def get_provider(config: dict, provider_name: str | None = None) -> Provider:
    """Get configured provider instance.

    Args:
        config: Configuration dictionary with API keys.
        provider_name: Provider name (mistral, openai, anthropic, gemini, mock).
                      Defaults to DEFAULT_PROVIDER if not specified.

    Returns:
        Configured Provider instance.

    Raises:
        ValueError: If provider is unknown or API key is missing.
    """
    name = provider_name or DEFAULT_PROVIDER

    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {name}. Available: {available}")

    # Some providers (e.g., mock) don't require an API key
    if name not in PROVIDER_API_KEYS:
        return PROVIDERS[name]()

    api_key_name = PROVIDER_API_KEYS[name]
    api_key = config.get(api_key_name.lower())

    if not api_key:
        api_key = os.getenv(api_key_name)

    if not api_key:
        raise ValueError(f"Missing API key for {name}. Set {api_key_name} environment variable.")

    return PROVIDERS[name](api_key=api_key)


def classify_email(provider: Provider, email_data: dict, prompt_template: str) -> dict:
    """Classify a single email using the provider."""
    prompt = prompt_template.format(
        sender=_sanitize_email_content(email_data["sender"], max_length=200),
        subject=_sanitize_email_content(email_data["subject"], max_length=500),
        date=email_data["date"],
        body=_sanitize_email_content(email_data["body"]),
    )

    result = provider.classify(prompt)

    return {
        "needs_action": result.needs_action,
        "priority": result.priority,
        "reason": result.reason,
    }


def classify_emails(config: dict, emails: list[dict], provider_name: str | None = None) -> list[dict]:
    """Classify all emails using the specified provider.

    Args:
        config: Configuration dictionary.
        emails: List of email dictionaries.
        provider_name: Provider to use (default: mistral).

    Returns:
        List of classified email dictionaries.
    """
    provider = get_provider(config, provider_name)
    prompt_template = load_prompt()
    results = []

    for i, email_data in enumerate(emails):
        result = classify_email(provider, email_data, prompt_template)
        results.append({
            **email_data,
            "needs_action": result.get("needs_action", False),
            "priority": result.get("priority", "low"),
            "reason": result.get("reason", ""),
        })

        # Simple rate limiting
        if i < len(emails) - 1:
            time.sleep(0.5)

    return results
