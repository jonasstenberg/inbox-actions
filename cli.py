"""Command-line interface for email classification."""

import argparse
import json

from config import get_config
from email_client import fetch_emails, list_folders, mark_emails
from classifier import classify_emails
from providers import PROVIDERS, DEFAULT_PROVIDER


def main():
    parser = argparse.ArgumentParser(
        description="Classify emails using IMAP and AI providers"
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDERS.keys()),
        default=DEFAULT_PROVIDER,
        help=f"AI provider to use (default: {DEFAULT_PROVIDER})",
    )
    parser.add_argument(
        "--unread-only", action="store_true", help="Only process unread emails"
    )
    parser.add_argument(
        "--limit", type=int, help="Max number of emails to process"
    )
    parser.add_argument(
        "--days", type=int, help="Fetch emails from last N days (default: 1)"
    )
    parser.add_argument(
        "--mark-read", action="store_true", help="Mark processed emails as read"
    )
    parser.add_argument(
        "--flag-action", action="store_true", help="Flag action-required emails"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Fetch emails without calling AI API"
    )
    parser.add_argument(
        "--list-folders", action="store_true", help="List available IMAP folders and exit"
    )
    parser.add_argument(
        "--notify-slack", action="store_true", help="Send Slack notification for action items"
    )
    parser.add_argument(
        "--notify-webhook", action="store_true", help="Send webhook notification for action items"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show debug output"
    )
    args = parser.parse_args()

    # Skip provider validation for dry-run mode
    provider_for_validation = None if args.dry_run else args.provider
    config = get_config(provider=provider_for_validation)

    if args.list_folders:
        list_folders(config)
        return

    if args.verbose:
        print(f"Fetching emails from {config['email_folder']}...")
    emails = fetch_emails(
        config,
        unread_only=args.unread_only,
        limit=args.limit,
        days=args.days,
        verbose=args.verbose,
    )

    if not emails:
        print("No emails found.")
        return

    if args.dry_run:
        if args.verbose:
            print(f"Found {len(emails)} emails (dry-run, skipping classification)")
        results = [
            {**e, "needs_action": False, "priority": "low", "reason": "dry-run mode"}
            for e in emails
        ]
    else:
        if args.verbose:
            print(f"Found {len(emails)} emails. Classifying with {args.provider}...")
        results = classify_emails(config, emails, provider_name=args.provider)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        from output import print_results
        print_results(results)

    if args.mark_read or args.flag_action:
        mark_emails(config, results, mark_read=args.mark_read, flag_action=args.flag_action)

    # Send notifications
    notifiers_to_enable = []
    if args.notify_slack:
        notifiers_to_enable.append("slack")
    if args.notify_webhook:
        notifiers_to_enable.append("webhook")

    if notifiers_to_enable:
        from notifications import NotificationManager
        manager = NotificationManager(notifiers=notifiers_to_enable, verbose=args.verbose)
        manager.send(results)


if __name__ == "__main__":
    main()
