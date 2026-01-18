"""Generic webhook notification backend."""

import json
import os
import urllib.request
import urllib.error

from notifications.base import Notifier

# Default timeout for webhook requests (in seconds)
DEFAULT_TIMEOUT = 10


class WebhookNotifier(Notifier):
    """Send notifications to a generic webhook endpoint."""

    def __init__(self, webhook_url: str | None = None, action_only: bool = True):
        """Initialize webhook notifier.

        Args:
            webhook_url: Webhook URL. Falls back to WEBHOOK_URL env var.
            action_only: If True, only send action-required items.
        """
        self.webhook_url = webhook_url or os.getenv("WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("Webhook URL required (pass or set WEBHOOK_URL)")
        self.action_only = action_only
        self.timeout = int(os.getenv("WEBHOOK_TIMEOUT", DEFAULT_TIMEOUT))

    def send(self, results: list[dict]) -> None:
        """Send classification results to webhook."""
        if self.action_only:
            items = self.filter_action_items(results)
        else:
            items = results

        if not items:
            return

        payload = json.dumps({
            "total_emails": len(results),
            "action_required": len(self.filter_action_items(results)),
            "emails": [
                {
                    "sender": item["sender"],
                    "subject": item["subject"],
                    "date": item["date"],
                    "needs_action": item.get("needs_action", False),
                    "priority": item.get("priority", "low"),
                    "reason": item.get("reason", ""),
                }
                for item in items
            ],
        }).encode("utf-8")

        req = urllib.request.Request(
            self.webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status != 200:
                    print(f"Webhook notification failed: {response.status}")
        except urllib.error.URLError as e:
            print(f"Webhook notification error: {e}")
