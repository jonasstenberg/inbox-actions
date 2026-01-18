"""Command-line interface for email classification."""

import argparse
import json

from config import get_config
from email_client import fetch_emails, list_folders, mark_emails
from classifier import classify_emails
from output import print_results


def main():
    parser = argparse.ArgumentParser(
        description="Classify emails using IMAP and Mistral API"
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
        "--dry-run", action="store_true", help="Fetch emails without calling Mistral API"
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

    config = get_config()

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
            print(f"Found {len(emails)} emails. Classifying...")
        results = classify_emails(config, emails)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results)

    if args.mark_read or args.flag_action:
        mark_emails(config, results, mark_read=args.mark_read, flag_action=args.flag_action)

    # Send notifications
    if args.notify_slack:
        try:
            from notifications import SlackNotifier
            SlackNotifier().send(results)
            if args.verbose:
                print("Slack notification sent.")
        except ValueError as e:
            print(f"Slack notification skipped: {e}")

    if args.notify_webhook:
        try:
            from notifications import WebhookNotifier
            WebhookNotifier().send(results)
            if args.verbose:
                print("Webhook notification sent.")
        except ValueError as e:
            print(f"Webhook notification skipped: {e}")


if __name__ == "__main__":
    main()
