"""Notification backends for email classification results."""

from notifications.base import Notifier
from notifications.slack import SlackNotifier
from notifications.webhook import WebhookNotifier

__all__ = ["Notifier", "SlackNotifier", "WebhookNotifier"]
