"""Base notifier interface."""

from abc import ABC, abstractmethod


class Notifier(ABC):
    """Abstract base class for notification backends."""

    @abstractmethod
    def send(self, results: list[dict]) -> None:
        """Send notification with classification results.

        Args:
            results: List of classified email dicts with keys:
                - sender, subject, date, body
                - needs_action, priority, reason
        """
        raise NotImplementedError

    def filter_action_items(self, results: list[dict]) -> list[dict]:
        """Filter to only action-required items."""
        return [r for r in results if r.get("needs_action")]
