#!/usr/bin/env python3
"""
Daily Teach Email Agent
Picks a fresh topic, researches it, writes an engaging email, and sends it via Gmail SMTP.
"""

import anyio
import json
import logging
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_DIR   = Path(__file__).parent
TOPICS_FILE   = PROJECT_DIR / "topics_used.txt"
PENDING_DIR   = PROJECT_DIR / "pending"
LOG_FILE      = PROJECT_DIR / "agent.log"
CONFIG_FILE   = PROJECT_DIR / "gmail_config.json"

EMAIL_FROM    = "peddireddy.saisathwik@gmail.com"
EMAIL_TO      = "peddireddy.saisathwik@gmail.com"
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def load_app_password() -> str:
    """Read the Gmail App Password from the config file."""
    if not CONFIG_FILE.exists():
        log.error(
            "Missing config file: %s\n"
            "Create it with: {\"app_password\": \"xxxx xxxx xxxx xxxx\"}\n"
            "Get an App Password at: https://myaccount.google.com/apppasswords",
            CONFIG_FILE,
        )
        sys.exit(1)
    cfg = json.loads(CONFIG_FILE.read_text())
    pw = cfg.get("app_password", "").strip()
    if not pw or pw == "xxxx xxxx xxxx xxxx":
        log.error("gmail_config.json exists but app_password is not set.")
        sys.exit(1)
    return pw


def read_used_topics() -> list[str]:
    if not TOPICS_FILE.exists():
        return []
    return [l.strip() for l in TOPICS_FILE.read_text().splitlines() if l.strip()]


def append_topic(topic: str) -> None:
    with TOPICS_FILE.open("a") as f:
        f.write(topic + "\n")


def send_email(subject: str, body_html: str, app_password: str) -> None:
    """Send the email via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(EMAIL_FROM, app_password)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    log.info("Email sent via SMTP ✓")


def build_prompt(used_topics: list[str]) -> str:
    used_block = (
        "\n".join(f"  - {t}" for t in used_topics)
        if used_topics
        else "  (none yet — this is the first email!)"
    )
    return f"""You are a daily curiosity email writer. Research one fascinating topic and write an email about it.

Save the result as three separate files in: `{PENDING_DIR}`

STEP 1 — PICK A TOPIC
Choose something that is:
- Specific and concrete (not "black holes" — more like "the Penrose process of extracting energy from a spinning black hole's ergosphere")
- From any field: biology, history, mathematics, linguistics, physics, economics, art history, geology, etc.
- Deeply surprising or counterintuitive to most people

Topics already covered (do NOT repeat or closely overlap):
{used_block}

STEP 2 — RESEARCH
Use WebSearch to find real facts. Look for:
- The weirdest or most counterintuitive aspect
- A specific number, scale, or comparison that makes it visceral
- A human story or discovery moment if one exists
Search at least twice to cross-check facts.

STEP 3 — WRITE THE EMAIL
Write 2–3 paragraphs with this character:
- Conversational — like a brilliant friend who just discovered something amazing
- Specific — actual numbers, names, places. No hand-waving.
- Surprising — go deeper than the first Wikipedia paragraph
- No jargon unless immediately explained in plain English

Also write a subject line that:
- Sparks instant curiosity without naming the topic directly
- Feels like a great documentary title, not a newsletter header

STEP 4 — SAVE AS THREE FILES
Use the Write tool to create exactly these three files:

1. `{PENDING_DIR}/topic.txt` — just the topic name, one line, nothing else

2. `{PENDING_DIR}/subject.txt` — just the subject line, one line, nothing else

3. `{PENDING_DIR}/body.html` — just the HTML email body, nothing else
   Use <p> tags for paragraphs, <strong> for emphasis, <em> for italics.
   Do not include <html>, <head>, or <body> tags — just the content paragraphs.

After writing all three files, confirm they were created successfully.
"""


async def run() -> None:
    log.info("─" * 60)
    log.info("Daily Teach starting — %s", datetime.now().strftime("%Y-%m-%d %H:%M"))

    app_password = load_app_password()
    used_topics  = read_used_topics()
    log.info("Topics used so far: %d", len(used_topics))

    PENDING_DIR.mkdir(exist_ok=True)

    prompt = build_prompt(used_topics)

    log.info("Launching research agent…")
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["WebSearch", "WebFetch", "Write"],
            permission_mode="bypassPermissions",
            cwd=str(PROJECT_DIR),
            max_turns=15,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text") and block.text:
                    snippet = block.text[:120].replace("\n", " ")
                    log.info("Agent: %s…", snippet)

        if isinstance(message, ResultMessage):
            log.info("Agent done. stop_reason=%s", message.stop_reason)

    # ── Read the three files the agent wrote ──────────────────────────────────
    topic_file   = PENDING_DIR / "topic.txt"
    subject_file = PENDING_DIR / "subject.txt"
    body_file    = PENDING_DIR / "body.html"

    for f in (topic_file, subject_file, body_file):
        if not f.exists():
            log.error("Agent did not create %s — check log above.", f)
            sys.exit(1)

    topic   = topic_file.read_text(encoding="utf-8").strip()
    subject = subject_file.read_text(encoding="utf-8").strip()
    body    = body_file.read_text(encoding="utf-8").strip()

    log.info("Topic:   %s", topic)
    log.info("Subject: %s", subject)

    # ── Send ──────────────────────────────────────────────────────────────────
    send_email(subject, body, app_password)

    # ── Record topic & clean up ───────────────────────────────────────────────
    append_topic(topic)
    log.info("Topic recorded in topics_used.txt")

    for f in (topic_file, subject_file, body_file):
        f.unlink(missing_ok=True)

    log.info("✓ All done!")


if __name__ == "__main__":
    anyio.run(run)
