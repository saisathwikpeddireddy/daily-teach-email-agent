#!/usr/bin/env bash
# Wrapper script for cron — loads the correct environment before running the agent.
# Cron runs in a minimal shell with none of your normal PATH or env vars.

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON="/Users/sathwik/anaconda3/bin/python3"
AGENT="$SCRIPT_DIR/daily_teach.py"
LOG="$SCRIPT_DIR/agent.log"

# ── Environment ──────────────────────────────────────────────────────────────
# Give cron a usable PATH (needed for the bundled claude binary's sub-processes)
export PATH="/Users/sathwik/anaconda3/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Load any shell env vars you've set (e.g. ANTHROPIC_API_KEY if you ever need it)
# The claude_agent_sdk uses Claude Code's built-in auth, so no API key is required.
# If you add one later, uncomment and set the line below:
# export ANTHROPIC_API_KEY="sk-ant-..."

# ── Run ──────────────────────────────────────────────────────────────────────
echo "$(date): run_agent.sh starting" >> "$LOG"
"$PYTHON" "$AGENT" >> "$LOG" 2>&1
EXIT_CODE=$?
echo "$(date): run_agent.sh finished (exit $EXIT_CODE)" >> "$LOG"
exit $EXIT_CODE
