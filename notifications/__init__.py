"""Notification backends for email classification results."""

import os
from typing import Callable

from notifications.base import Notifier
from notifications.slack import SlackNotifier
from notifications.webhook import WebhookNotifier


# Registry of available notifiers
NOTIFIERS: dict[str, type[Notifier]] = {
    "slack": SlackNotifier,
    "webhook": WebhookNotifier,
}

# Environment variable names that enable each notifier
# If the env var is set, the notifier can be instantiated
NOTIFIER_ENV_VARS: dict[str, list[str]] = {
    "slack": ["SLACK_BOT_TOKEN", "SLACK_CHANNEL"],
    "webhook": ["WEBHOOK_URL"],
}


class NotificationManager:
    """Centralized manager for notification backends.

    Handles notifier instantiation, configuration, and dispatching
    notifications to multiple backends with proper error handling.
    """

    def __init__(
        self,
        notifiers: list[str] | None = None,
        verbose: bool = False,
        on_error: Callable[[str, Exception], None] | None = None,
    ):
        """Initialize the notification manager.

        Args:
            notifiers: List of notifier names to enable (e.g., ["slack", "webhook"]).
                      If None, no notifiers are enabled.
            verbose: If True, print success messages after sending.
            on_error: Optional callback for handling errors. Receives notifier name
                     and exception. If None, errors are printed to stdout.
        """
        self.verbose = verbose
        self.on_error = on_error or self._default_error_handler
        self._notifiers: list[tuple[str, Notifier]] = []

        if notifiers:
            for name in notifiers:
                self._register_notifier(name)

    def _default_error_handler(self, name: str, error: Exception) -> None:
        """Default error handler that prints to stdout."""
        print(f"{name.capitalize()} notification skipped: {error}")

    def _register_notifier(self, name: str) -> None:
        """Attempt to instantiate and register a notifier.

        Args:
            name: The notifier name from NOTIFIERS registry.

        Raises:
            ValueError: If the notifier name is not in the registry.
        """
        if name not in NOTIFIERS:
            raise ValueError(
                f"Unknown notifier: {name}. Available: {list(NOTIFIERS.keys())}"
            )

        notifier_class = NOTIFIERS[name]
        try:
            notifier = notifier_class()
            self._notifiers.append((name, notifier))
        except ValueError as e:
            self.on_error(name, e)

    def send(self, results: list[dict]) -> dict[str, bool]:
        """Send notifications to all registered backends.

        Args:
            results: List of classified email dicts.

        Returns:
            Dict mapping notifier names to success status.
        """
        statuses: dict[str, bool] = {}

        for name, notifier in self._notifiers:
            try:
                notifier.send(results)
                statuses[name] = True
                if self.verbose:
                    print(f"{name.capitalize()} notification sent.")
            except Exception as e:
                statuses[name] = False
                self.on_error(name, e)

        return statuses

    @property
    def active_notifiers(self) -> list[str]:
        """Return list of successfully registered notifier names."""
        return [name for name, _ in self._notifiers]

    @classmethod
    def from_env(cls, verbose: bool = False) -> "NotificationManager":
        """Create a NotificationManager with notifiers auto-detected from environment.

        Checks NOTIFIER_ENV_VARS to determine which notifiers have their
        required environment variables set.

        Args:
            verbose: If True, print success messages after sending.

        Returns:
            NotificationManager with auto-detected notifiers.
        """
        enabled = []
        for name, env_vars in NOTIFIER_ENV_VARS.items():
            if all(os.getenv(var) for var in env_vars):
                enabled.append(name)
        return cls(notifiers=enabled, verbose=verbose)


def get_notifier(name: str) -> Notifier:
    """Get a notifier instance by name.

    Args:
        name: The notifier name (e.g., "slack", "webhook").

    Returns:
        An instantiated Notifier.

    Raises:
        ValueError: If the notifier name is unknown or configuration is missing.
    """
    if name not in NOTIFIERS:
        raise ValueError(
            f"Unknown notifier: {name}. Available: {list(NOTIFIERS.keys())}"
        )
    return NOTIFIERS[name]()


__all__ = [
    "Notifier",
    "SlackNotifier",
    "WebhookNotifier",
    "NotificationManager",
    "NOTIFIERS",
    "NOTIFIER_ENV_VARS",
    "get_notifier",
]
