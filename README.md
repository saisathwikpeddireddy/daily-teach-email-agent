# Daily Teach Email Agent

> **As a curious person who wants to keep learning but never has time to go looking,**
> **I want a short, surprising email waiting in my inbox every morning**
> **so that I start my day knowing something I didn't know yesterday — without any effort on my part.**

A Python agent that emails you one genuinely fascinating thing every day at 9am IST. It picks a topic it hasn't covered before, researches it on the web, and writes three short punchy paragraphs — conversational, specific, and surprising. Not textbook facts. The kind of thing you'd text a friend.

Runs entirely on GitHub Actions — no laptop required.

**Example subjects it has sent:**
- *Why Every GPS Satellite Clock Is Deliberately Set to the Wrong Time*
- *Why the Fastest Thing in the Universe Has a 100,000-Year Commute*
- *The 117,000-Year Catastrophe That Almost Erased Us*

---

## How it works

1. Reads `topics_used.txt` to see what's already been covered
2. Launches a Claude agent (via `claude_agent_sdk`) that searches the web, picks a novel topic, and writes the email
3. Sends it via Gmail SMTP
4. Appends the topic to `topics_used.txt` and commits it back to the repo so it never repeats
5. Triggered every day at 9am IST by a GitHub Actions scheduled workflow — your laptop never needs to be on

---

## Setup

### 1. Fork this repo

### 2. Add two GitHub Actions secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your key from [console.anthropic.com](https://console.anthropic.com) |
| `GMAIL_APP_PASSWORD` | A Gmail App Password (see below) |

### 3. Create a Gmail App Password

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Create a new App Password (name it anything, e.g. "Daily Teach")
3. Copy the 16-character password — that's your `GMAIL_APP_PASSWORD`

### 4. Edit the email address

In `daily_teach.py`, update these two lines to your Gmail address:

```python
EMAIL_FROM = "you@gmail.com"
EMAIL_TO   = "you@gmail.com"
```

### 5. Enable Actions

Go to the **Actions** tab in your repo and enable workflows if prompted. The schedule will kick in automatically — first email arrives the next morning at 9am IST.

---

## Run it manually

Trigger a run anytime from the **Actions** tab → **Daily Teach Email** → **Run workflow**.

Or locally:

```bash
pip install anthropic claude-agent-sdk
python3 daily_teach.py
```

---

## Files

| File | Purpose |
|---|---|
| `daily_teach.py` | Main agent — research, write, send |
| `.github/workflows/daily_teach.yml` | GitHub Actions schedule (9am IST daily) |
| `topics_used.txt` | One topic per line, committed after each send |
| `run_agent.sh` | Optional local cron wrapper |
| `gmail_config.json` | Gmail App Password for local runs — **gitignored, never commit** |

---

## Requirements

- Python 3.11+
- An Anthropic API key
- A Gmail account with [App Passwords](https://myaccount.google.com/apppasswords) enabled (requires 2FA)
