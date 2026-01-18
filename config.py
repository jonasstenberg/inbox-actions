"""Configuration loading from environment variables."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def get_config():
    """Load configuration from environment variables."""
    required = ["IMAP_SERVER", "IMAP_USERNAME", "IMAP_PASSWORD", "MISTRAL_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    return {
        "imap_server": os.getenv("IMAP_SERVER"),
        "imap_username": os.getenv("IMAP_USERNAME"),
        "imap_password": os.getenv("IMAP_PASSWORD"),
        "mistral_api_key": os.getenv("MISTRAL_API_KEY"),
        "email_folder": os.getenv("EMAIL_FOLDER", "INBOX"),
        "email_limit": int(os.getenv("EMAIL_LIMIT", 10)),
        "email_days": int(os.getenv("EMAIL_DAYS", 1)),
    }
