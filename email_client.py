"""IMAP email operations."""

import os
import ssl
import sys
from datetime import datetime, timedelta

from imap_tools import AND, MailBox

# Default max email size: 1MB (prevents loading huge emails into memory)
DEFAULT_MAX_EMAIL_SIZE = 1 * 1024 * 1024  # 1MB in bytes
# Body truncation limit for classifier
BODY_TRUNCATE_LENGTH = 1500


def _get_ssl_context():
    """Create SSL context with certificate verification."""
    return ssl.create_default_context()


def _get_max_email_size():
    """Get maximum email size from environment or use default."""
    env_size = os.getenv("EMAIL_MAX_SIZE")
    if env_size:
        try:
            return int(env_size)
        except ValueError:
            print(f"Warning: Invalid EMAIL_MAX_SIZE '{env_size}', using default {DEFAULT_MAX_EMAIL_SIZE}")
    return DEFAULT_MAX_EMAIL_SIZE


def fetch_emails(config, unread_only=False, limit=None, days=None, verbose=False):
    """Fetch emails from IMAP server.

    Uses a two-phase fetch to avoid loading large emails into memory:
    1. First fetches headers only to check email sizes
    2. Then fetches full content only for emails under the size limit
    """
    limit = limit or config["email_limit"]
    days = days or config["email_days"]
    max_size = _get_max_email_size()
    emails = []
    since_date = (datetime.now() - timedelta(days=days)).date()

    try:
        with MailBox(config["imap_server"], ssl_context=_get_ssl_context()).login(
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

            # Phase 1: Fetch headers only to get sizes and UIDs
            headers_data = []
            for msg in mailbox.fetch(criteria, reverse=True, limit=limit, headers_only=True):
                headers_data.append({
                    "uid": msg.uid,
                    "subject": msg.subject or "(no subject)",
                    "sender": msg.from_,
                    "date": msg.date,
                    "size": msg.size_rfc822 or 0,
                })

            # Phase 2: Fetch full content only for small emails
            small_uids = []
            skipped_count = 0
            for hdr in headers_data:
                if hdr["size"] <= max_size:
                    small_uids.append(hdr["uid"])
                else:
                    skipped_count += 1
                    if verbose:
                        size_mb = hdr["size"] / (1024 * 1024)
                        print(f"  Skipping large email ({size_mb:.1f}MB): {hdr['subject'][:50]}")
                    # Add placeholder for large emails with metadata only
                    date_str = hdr["date"].strftime("%Y-%m-%d %H:%M") if hdr["date"] else "Unknown"
                    emails.append({
                        "uid": hdr["uid"],
                        "sender": hdr["sender"],
                        "subject": hdr["subject"],
                        "date": date_str,
                        "body": f"[Email too large to process: {hdr['size'] / (1024 * 1024):.1f}MB]",
                    })

            if skipped_count > 0 and not verbose:
                print(f"  Warning: Skipped {skipped_count} email(s) exceeding size limit ({max_size / (1024 * 1024):.1f}MB)")

            # Fetch full content for small emails
            if small_uids:
                for i, msg in enumerate(mailbox.fetch(AND(uid=small_uids))):
                    date_str = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "Unknown"
                    body = (msg.text or msg.html or "")[:BODY_TRUNCATE_LENGTH]

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
        with MailBox(config["imap_server"], ssl_context=_get_ssl_context()).login(
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
        with MailBox(config["imap_server"], ssl_context=_get_ssl_context()).login(
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
