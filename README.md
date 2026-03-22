# Daily Teach Email Agent

A Python agent that emails you one genuinely fascinating thing every day at 9am. It picks a topic it hasn't covered before, researches it on the web, and writes 2–3 engaging paragraphs — conversational, specific, and surprising. Not textbook facts. The kind of thing you'd text a friend.

**Example subjects it has sent:**
- *Why Every GPS Satellite Clock Is Deliberately Set to the Wrong Time*
- *Why the Fastest Thing in the Universe Has a 100,000-Year Commute*

---

## How it works

1. Reads `topics_used.txt` to see what's already been covered
2. Launches a Claude agent (via `claude_agent_sdk`) that searches the web, picks a novel topic, and writes the email
3. Sends it via Gmail SMTP
4. Appends the topic to `topics_used.txt` so it never repeats
5. Runs automatically every day at 9am via a cron job — no apps need to be open

---

## Setup

### 1. Install dependencies

```bash
pip install anthropic claude-agent-sdk
```

### 2. Create your Gmail App Password

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Create a new App Password (name it anything, e.g. "Daily Teach")
3. Copy the 16-character password

### 3. Create `gmail_config.json`

```json
{
  "app_password": "xxxx xxxx xxxx xxxx"
}
```

> This file is gitignored — never commit it.

### 4. Edit the email address

In `daily_teach.py`, update these two lines to your Gmail address:

```python
EMAIL_FROM = "you@gmail.com"
EMAIL_TO   = "you@gmail.com"
```

### 5. Set up the cron job

```bash
crontab -e
```

Add this line (update the path to match where you cloned the repo):

```
0 9 * * * "/path/to/daily-teach-email-agent/run_agent.sh"
```

That's it. Your Mac just needs to be on and awake at 9am.

---

## Run it manually

```bash
python3 daily_teach.py
```

---

## Files

| File | Purpose |
|---|---|
| `daily_teach.py` | Main agent — research, write, send |
| `run_agent.sh` | Cron-safe shell wrapper (sets correct PATH for headless runs) |
| `topics_used.txt` | One topic per line, appended after each send |
| `gmail_config.json` | Your Gmail App Password — **gitignored, never commit** |
| `agent.log` | Runtime log for debugging |

---

## Requirements

- Python 3.11+
- [Claude Code](https://claude.ai/code) installed (the agent SDK uses its bundled binary)
- A Gmail account with [App Passwords](https://myaccount.google.com/apppasswords) enabled (requires 2FA)
