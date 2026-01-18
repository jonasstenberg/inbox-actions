# Inbox Actions

A CLI tool that fetches emails via IMAP and classifies them using Mistral AI to identify action items.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your credentials:
   - `IMAP_SERVER` - Your IMAP server (e.g., `imap.gmail.com`)
   - `IMAP_USERNAME` - Your email address
   - `IMAP_PASSWORD` - Your email password or app-specific password
   - `MISTRAL_API_KEY` - Your Mistral API key

## Usage

Basic usage:
```bash
python main.py
```

### Options

| Flag | Description |
|------|-------------|
| `--unread-only` | Only process unread emails |
| `--limit N` | Max number of emails to process |
| `--days N` | Fetch emails from last N days (default: 1) |
| `--mark-read` | Mark processed emails as read |
| `--flag-action` | Flag emails that require action |
| `--json` | Output results as JSON |
| `--dry-run` | Fetch emails without calling Mistral API |
| `--list-folders` | List available IMAP folders and exit |
| `--notify-slack` | Send Slack notification for action items |
| `--notify-webhook` | Send webhook notification for action items |
| `-v, --verbose` | Show debug output |

### Examples

Process last 5 unread emails:
```bash
python main.py --unread-only --limit 5
```

List available mail folders:
```bash
python main.py --list-folders
```

Get JSON output for the last 3 days:
```bash
python main.py --days 3 --json
```
