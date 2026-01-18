"""Slack notification backend."""

import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from notifications.base import Notifier


class SlackNotifier(Notifier):
    """Send notifications to Slack via Bot token."""

    def __init__(self, token: str | None = None, channel: str | None = None):
        """Initialize Slack notifier.

        Args:
            token: Slack Bot token (xoxb-...). Falls back to SLACK_BOT_TOKEN env var.
            channel: Channel ID or name. Falls back to SLACK_CHANNEL env var.
        """
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = channel or os.getenv("SLACK_CHANNEL")
        if not self.token:
            raise ValueError("Slack bot token required (pass or set SLACK_BOT_TOKEN)")
        if not self.channel:
            raise ValueError("Slack channel required (pass or set SLACK_CHANNEL)")
        self.client = WebClient(token=self.token)

    def send(self, results: list[dict]) -> None:
        """Send classification results to Slack."""
        action_items = self.filter_action_items(results)

        if not action_items:
            return

        blocks = self._build_message(action_items, len(results))

        try:
            self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=f"{len(action_items)} emails need action",
            )
        except SlackApiError as e:
            print(f"Slack notification failed: {e.response['error']}")

    def _build_message(self, action_items: list[dict], total: int) -> list[dict]:
        """Build Slack block kit message."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📬 {len(action_items)} emails need action",
                },
            },
        ]

        for item in action_items[:5]:  # Limit to 5 items
            priority = item.get("priority", "low").upper()
            emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(priority, "⚪")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{priority}*: {item['subject']}\n"
                            f"From: {item['sender']}\n"
                            f"_{item.get('reason', '')}_",
                },
            })

        if len(action_items) > 5:
            blocks.append({
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"_...and {len(action_items) - 5} more_"},
                ],
            })

        return blocks
