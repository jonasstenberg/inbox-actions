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

## Scheduling

### macOS (launchd)

1. Create a plist file:

   ```bash
   cat > ~/Library/LaunchAgents/com.inbox-actions.plist << 'EOF'
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.inbox-actions</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>/path/to/inbox-actions/main.py</string>
           <string>--unread-only</string>
           <string>--notify-slack</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/path/to/inbox-actions</string>
       <key>StartCalendarInterval</key>
       <dict>
           <key>Hour</key>
           <integer>8</integer>
           <key>Minute</key>
           <integer>0</integer>
       </dict>
       <key>StandardOutPath</key>
       <string>/tmp/inbox-actions.log</string>
       <key>StandardErrorPath</key>
       <string>/tmp/inbox-actions.err</string>
   </dict>
   </plist>
   EOF
   ```

2. Update the paths in the plist to match your installation.

3. Load the job (modern syntax):

   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.inbox-actions.plist
   ```

4. To unload:

   ```bash
   launchctl bootout gui/$(id -u)/com.inbox-actions
   ```

5. To check status:

   ```bash
   launchctl print gui/$(id -u)/com.inbox-actions
   ```

### Linux (cron)

1. Open your crontab:

   ```bash
   crontab -e
   ```

2. Add a line to run daily at 8am:

   ```cron
   0 8 * * * cd /path/to/inbox-actions && /usr/bin/python3 main.py --unread-only --notify-slack >> /tmp/inbox-actions.log 2>&1
   ```

### Linux (systemd timer)

1. Create a service file at `~/.config/systemd/user/inbox-actions.service`:

   ```ini
   [Unit]
   Description=Inbox Actions Email Classifier

   [Service]
   Type=oneshot
   WorkingDirectory=/path/to/inbox-actions
   ExecStart=/usr/bin/python3 main.py --unread-only --notify-slack
   ```

2. Create a timer file at `~/.config/systemd/user/inbox-actions.timer`:

   ```ini
   [Unit]
   Description=Run Inbox Actions daily at 8am

   [Timer]
   OnCalendar=*-*-* 08:00:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   ```

3. Enable and start the timer:

   ```bash
   systemctl --user daemon-reload
   systemctl --user enable inbox-actions.timer
   systemctl --user start inbox-actions.timer
   ```

4. Check status:

   ```bash
   systemctl --user status inbox-actions.timer
   systemctl --user list-timers
   ```
