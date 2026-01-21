"""Configuration loading from environment variables."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def get_config(provider: str | None = None):
    """Load configuration from environment variables.

    Args:
        provider: The AI provider to use. If specified, validates that
                 the provider's API key is set. If None, uses lazy validation
                 (API key checked when provider is instantiated).

    Returns:
        Configuration dictionary.
    """
    # Always required: IMAP credentials
    required = ["IMAP_SERVER", "IMAP_USERNAME", "IMAP_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    # Provider API key validation (lazy - only check selected provider)
    from providers import PROVIDER_API_KEYS, DEFAULT_PROVIDER

    selected_provider = provider or DEFAULT_PROVIDER
    if selected_provider in PROVIDER_API_KEYS:
        api_key_var = PROVIDER_API_KEYS[selected_provider]
        if not os.getenv(api_key_var):
            print(f"Error: Missing {api_key_var} for provider '{selected_provider}'")
            print(f"Set {api_key_var} in your .env file or environment.")
            sys.exit(1)

    return {
        "imap_server": os.getenv("IMAP_SERVER"),
        "imap_port": int(os.getenv("IMAP_PORT", 993)),
        "imap_username": os.getenv("IMAP_USERNAME"),
        "imap_password": os.getenv("IMAP_PASSWORD"),
        "imap_starttls": os.getenv("IMAP_STARTTLS", "false").lower() == "true",
        "mistral_api_key": os.getenv("MISTRAL_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "email_folder": os.getenv("EMAIL_FOLDER", "INBOX"),
        "email_limit": int(os.getenv("EMAIL_LIMIT", 10)),
        "email_days": int(os.getenv("EMAIL_DAYS", 1)),
    }
