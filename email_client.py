"""IMAP email operations."""

import os
import ssl
import sys
from datetime import datetime, timedelta

from imap_tools import AND, MailBox, MailBoxStartTls

# Default max email size: 1MB (prevents loading huge emails into memory)
DEFAULT_MAX_EMAIL_SIZE = 1 * 1024 * 1024  # 1MB in bytes
# Body truncation limit for classifier
BODY_TRUNCATE_LENGTH = 1500


def _get_ssl_context(allow_self_signed=False):
    """Create SSL context with certificate verification."""
    ctx = ssl.create_default_context()
    if allow_self_signed:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get_mailbox(config):
    """Create appropriate mailbox connection based on config."""
    if config.get("imap_starttls"):
        # STARTTLS connection (e.g., Proton Bridge)
        return MailBoxStartTls(
            config["imap_server"],
            port=config.get("imap_port", 1143),
            ssl_context=_get_ssl_context(allow_self_signed=True),
        )
    else:
        # Direct SSL/TLS connection (standard IMAP)
        return MailBox(
            config["imap_server"],
            port=config.get("imap_port", 993),
            ssl_context=_get_ssl_context(),
        )


def _get_max_email_size():
    """Get maximum email size from environment or use default."""
    env_size = os.getenv("EMAIL_MAX_SIZE")
    if env_size:
        try:
            return int(env_size)
        except ValueError:
            print(f"Warning: Invalid EMAIL_MAX_SIZE '{env_size}', using default {DEFAULT_MAX_EMAIL_SIZE}")
    return DEFAULT_MAX_EMAIL_SIZE


def _fetch_headers(mailbox, criteria, limit):
    """Phase 1: Fetch email headers only to get sizes and UIDs.

    Returns:
        List of header dicts with uid, subject, sender, date, size.
    """
    headers = []
    for msg in mailbox.fetch(criteria, reverse=True, limit=limit, headers_only=True):
        headers.append({
            "uid": msg.uid,
            "subject": msg.subject or "(no subject)",
            "sender": msg.from_,
            "date": msg.date,
            "size": msg.size_rfc822 or 0,
        })
    return headers


def _filter_by_size(headers, max_size, verbose):
    """Phase 2: Filter emails by size and create placeholders for large ones.

    Returns:
        Tuple of (small_uids list, large_email_placeholders list).
    """
    small_uids = []
    placeholders = []

    for hdr in headers:
        if hdr["size"] <= max_size:
            small_uids.append(hdr["uid"])
        else:
            if verbose:
                size_mb = hdr["size"] / (1024 * 1024)
                print(f"  Skipping large email ({size_mb:.1f}MB): {hdr['subject'][:50]}")
            date_str = hdr["date"].strftime("%Y-%m-%d %H:%M") if hdr["date"] else "Unknown"
            placeholders.append({
                "uid": hdr["uid"],
                "sender": hdr["sender"],
                "subject": hdr["subject"],
                "date": date_str,
                "body": f"[Email too large to process: {hdr['size'] / (1024 * 1024):.1f}MB]",
            })

    return small_uids, placeholders


def _fetch_full_content(mailbox, uids, verbose):
    """Phase 3: Fetch full email content for the given UIDs.

    Returns:
        List of email dicts with uid, sender, subject, date, body.
    """
    emails = []
    for i, msg in enumerate(mailbox.fetch(AND(uid=uids))):
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

    return emails


def fetch_emails(config, unread_only=False, limit=None, days=None, verbose=False):
    """Fetch emails from IMAP server.

    Uses a two-phase fetch to avoid loading large emails into memory:
    1. First fetches headers only to check email sizes
    2. Then fetches full content only for emails under the size limit
    """
    limit = limit or config["email_limit"]
    days = days or config["email_days"]
    max_size = _get_max_email_size()
    since_date = (datetime.now() - timedelta(days=days)).date()

    criteria = AND(seen=False, date_gte=since_date) if unread_only else AND(date_gte=since_date)

    if verbose:
        print(f"  Fetching emails since {since_date} (up to {limit})...")

    try:
        with _get_mailbox(config).login(
            config["imap_username"],
            config["imap_password"],
            config["email_folder"],
        ) as mailbox:
            headers = _fetch_headers(mailbox, criteria, limit)
            small_uids, large_placeholders = _filter_by_size(headers, max_size, verbose)

            skipped_count = len(large_placeholders)
            if skipped_count > 0 and not verbose:
                print(f"  Warning: Skipped {skipped_count} email(s) exceeding size limit ({max_size / (1024 * 1024):.1f}MB)")

            emails = large_placeholders
            if small_uids:
                emails.extend(_fetch_full_content(mailbox, small_uids, verbose))

            return emails

    except Exception as e:
        print(f"IMAP error: {e}")
        sys.exit(1)


def list_folders(config):
    """List available IMAP folders."""
    try:
        with _get_mailbox(config).login(
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
        with _get_mailbox(config).login(
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
