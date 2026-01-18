# Inbox Actions

A CLI tool that fetches emails via IMAP and classifies them using AI to identify action items.

## Supported AI Providers

- **Ollama** (default) - `llama3.2` (local, no API key required)
- **Mistral** - `mistral-medium-latest`
- **OpenAI** - `gpt-5-mini`
- **Anthropic** - `claude-haiku-4.5`
- **Gemini** - `gemini-2.5-flash`
- **Mock** - For testing without API calls (deterministic fake responses)

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
   - For cloud providers, set the appropriate API key (see `.env.example`)

4. For local inference (default), install and run [Ollama](https://ollama.ai/):

   ```bash
   ollama pull llama3.2
   ollama serve
   ```

## Usage

Basic usage (uses Ollama by default):

```bash
python main.py
```

Use a cloud provider:

```bash
python main.py --provider mistral
python main.py --provider openai
python main.py --provider anthropic
python main.py --provider gemini
```

### Options

| Flag               | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| `--provider`       | AI provider: `ollama`, `mistral`, `openai`, `anthropic`, `gemini` (default: ollama) |
| `--unread-only`    | Only process unread emails                                                        |
| `--limit N`        | Max number of emails to process                                                   |
| `--days N`         | Fetch emails from last N days (default: 1)                                        |
| `--mark-read`      | Mark processed emails as read                                                     |
| `--flag-action`    | Flag emails that require action                                                   |
| `--json`           | Output results as JSON                                                            |
| `--dry-run`        | Fetch emails without calling AI API                                               |
| `--list-folders`   | List available IMAP folders and exit                                              |
| `--notify-slack`   | Send Slack notification for action items                                          |
| `--notify-webhook` | Send webhook notification for action items                                        |
| `-v, --verbose`    | Show debug output                                                                 |

### Examples

Process last 5 unread emails:

```bash
python main.py --unread-only --limit 5
```

Use OpenAI with verbose output:

```bash
python main.py --provider openai -v
```

List available mail folders:

```bash
python main.py --list-folders
```

Get JSON output for the last 3 days:

```bash
python main.py --days 3 --json
```

Test the pipeline without API calls:

```bash
python main.py --provider mock
```
