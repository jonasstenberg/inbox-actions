"""IMAP email operations."""

import sys
from datetime import datetime, timedelta

from imap_tools import AND, MailBox


def fetch_emails(config, unread_only=False, limit=None, days=None, verbose=False):
    """Fetch emails from IMAP server."""
    limit = limit or config["email_limit"]
    days = days or config["email_days"]
    emails = []
    since_date = (datetime.now() - timedelta(days=days)).date()

    try:
        with MailBox(config["imap_server"]).login(
            config["imap_username"],
            config["imap_password"],
            config["email_folder"],
        ) as mailbox:
            if unread_only:
                criteria = AND(seen=False, date_gte=since_date)
            else:
                criteria = AND(date_gte=since_date)

            if verbose:
                print(f"  Fetching emails since {since_date} (up to {limit})...")

            for i, msg in enumerate(mailbox.fetch(criteria, reverse=True, limit=limit)):
                date_str = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "Unknown"
                body = (msg.text or msg.html or "")[:1500]

                emails.append({
                    "uid": msg.uid,
                    "sender": msg.from_,
                    "subject": msg.subject or "(no subject)",
                    "date": date_str,
                    "body": body,
                })

                if verbose and i < 2:
                    print(f"  Fetched: {msg.subject[:50] if msg.subject else '(no subject)'}")

    except Exception as e:
        print(f"IMAP error: {e}")
        sys.exit(1)

    return emails


def list_folders(config):
    """List available IMAP folders."""
    try:
        with MailBox(config["imap_server"]).login(
            config["imap_username"],
            config["imap_password"],
        ) as mailbox:
            print("Available folders:")
            for folder in mailbox.folder.list():
                print(f"  {folder.name}")

    except Exception as e:
        print(f"Error listing folders: {e}")
        sys.exit(1)


def mark_emails(config, results, mark_read=False, flag_action=False):
    """Mark processed emails as read or flag action-required ones."""
    if not mark_read and not flag_action:
        return

    try:
        with MailBox(config["imap_server"]).login(
            config["imap_username"],
            config["imap_password"],
            config["email_folder"],
        ) as mailbox:
            for r in results:
                uid = r["uid"]
                if mark_read:
                    mailbox.flag(uid, "\\Seen", True)
                if flag_action and r.get("needs_action"):
                    mailbox.flag(uid, "\\Flagged", True)

        print(f"Updated email flags (mark_read={mark_read}, flag_action={flag_action})")

    except Exception as e:
        print(f"Warning: Failed to update email flags: {e}")
