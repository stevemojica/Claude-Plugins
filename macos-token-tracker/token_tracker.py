#!/usr/bin/env python3
"""
Claude Token Usage Tracker — macOS Menu Bar App

Tracks your Anthropic API token usage via rate-limit headers and local
logging. Works with any personal API key (sk-ant-api...).

Every refresh, the app makes one minimal API call to read the rate-limit
headers returned by the Anthropic API, which tell you:
  - Token limit, remaining tokens, and when the limit resets
  - Request limit, remaining requests, and when the request limit resets

It also keeps a local SQLite log of every check so you can see usage
trends over time (today, 7-day, 30-day).
"""

import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import rumps
from dateutil import parser as dtparser

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".claude-token-tracker"
CONFIG_FILE = CONFIG_DIR / "config.json"
DB_FILE = CONFIG_DIR / "usage.db"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def load_config():
    config = {
        "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "refresh_minutes": 5,
        "model": "claude-haiku-4-5-20251001",  # cheapest model for the probe call
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                saved = json.load(f)
            config.update(saved)
        except Exception:
            pass
    return config


def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# ---------------------------------------------------------------------------
# Local SQLite usage log
# ---------------------------------------------------------------------------


def init_db():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            model TEXT,
            req_limit INTEGER,
            req_remaining INTEGER,
            req_reset TEXT,
            tok_limit INTEGER,
            tok_remaining INTEGER,
            tok_reset TEXT
        )"""
    )
    conn.commit()
    return conn


def log_usage(conn, data: dict):
    conn.execute(
        """INSERT INTO usage_log
           (timestamp, input_tokens, output_tokens, model,
            req_limit, req_remaining, req_reset,
            tok_limit, tok_remaining, tok_reset)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["timestamp"],
            data["input_tokens"],
            data["output_tokens"],
            data["model"],
            data.get("req_limit"),
            data.get("req_remaining"),
            data.get("req_reset"),
            data.get("tok_limit"),
            data.get("tok_remaining"),
            data.get("tok_reset"),
        ),
    )
    conn.commit()


def query_usage(conn, since_hours: int) -> dict:
    """Sum tokens logged in the last N hours."""
    cutoff = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # SQLite datetime comparison works with ISO strings
    from datetime import timedelta

    cutoff_dt = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    cutoff = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    row = conn.execute(
        """SELECT COALESCE(SUM(input_tokens), 0),
                  COALESCE(SUM(output_tokens), 0),
                  COUNT(*)
           FROM usage_log WHERE timestamp >= ?""",
        (cutoff,),
    ).fetchone()
    return {"input": row[0], "output": row[1], "calls": row[2]}


# ---------------------------------------------------------------------------
# Anthropic API probe — minimal call to read rate-limit headers
# ---------------------------------------------------------------------------


def probe_rate_limits(api_key: str, model: str) -> dict:
    """Make a tiny API call and return rate-limit info + token usage."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    # Smallest possible valid request — 1 token max output
    body = {
        "model": model,
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "hi"}],
    }
    resp = requests.post(ANTHROPIC_API_URL, json=body, headers=headers, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    h = resp.headers

    usage = data.get("usage", {})
    result = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "model": model,
        # Rate-limit headers
        "req_limit": _int(h.get("anthropic-ratelimit-requests-limit")),
        "req_remaining": _int(h.get("anthropic-ratelimit-requests-remaining")),
        "req_reset": h.get("anthropic-ratelimit-requests-reset", ""),
        "tok_limit": _int(h.get("anthropic-ratelimit-tokens-limit")),
        "tok_remaining": _int(h.get("anthropic-ratelimit-tokens-remaining")),
        "tok_reset": h.get("anthropic-ratelimit-tokens-reset", ""),
    }
    return result


def _int(val):
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def fmt_pct(remaining, limit) -> str:
    if not limit or not remaining:
        return "—"
    used = limit - remaining
    pct = (used / limit) * 100
    return f"{pct:.0f}%"


def time_until_reset(reset_str: str) -> str:
    """Parse an ISO reset timestamp and return a human countdown."""
    if not reset_str:
        return "unknown"
    try:
        reset_dt = dtparser.isoparse(reset_str)
        if reset_dt.tzinfo is None:
            reset_dt = reset_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = reset_dt - now
        if delta.total_seconds() <= 0:
            return "now"
        total_secs = int(delta.total_seconds())
        if total_secs < 60:
            return f"{total_secs}s"
        mins, secs = divmod(total_secs, 60)
        if mins < 60:
            return f"{mins}m {secs}s"
        hours, mins = divmod(mins, 60)
        if hours < 24:
            return f"{hours}h {mins}m"
        days = hours // 24
        hours = hours % 24
        return f"{days}d {hours}h"
    except Exception:
        return reset_str


# ---------------------------------------------------------------------------
# Menu Bar App
# ---------------------------------------------------------------------------


class TokenTrackerApp(rumps.App):
    def __init__(self):
        super().__init__("⏳", quit_button=None)
        self.config = load_config()
        self.db = init_db()
        self.last_probe = None
        self.last_error = None

        # --- Menu items ---
        self.title_item = rumps.MenuItem("Claude Token Tracker")
        self.title_item.set_callback(None)

        # Rate limits section
        self.rl_header = rumps.MenuItem("— Rate Limits —")
        self.rl_header.set_callback(None)

        self.tok_limit_item = rumps.MenuItem("Token limit: loading...")
        self.tok_limit_item.set_callback(None)
        self.tok_remaining_item = rumps.MenuItem("Tokens remaining: loading...")
        self.tok_remaining_item.set_callback(None)
        self.tok_used_item = rumps.MenuItem("Tokens used: loading...")
        self.tok_used_item.set_callback(None)
        self.tok_reset_item = rumps.MenuItem("Token reset: loading...")
        self.tok_reset_item.set_callback(None)

        self.req_limit_item = rumps.MenuItem("Request limit: loading...")
        self.req_limit_item.set_callback(None)
        self.req_remaining_item = rumps.MenuItem("Requests remaining: loading...")
        self.req_remaining_item.set_callback(None)
        self.req_reset_item = rumps.MenuItem("Request reset: loading...")
        self.req_reset_item.set_callback(None)

        # Local usage tracking section
        self.usage_header = rumps.MenuItem("— Tracked Usage —")
        self.usage_header.set_callback(None)
        self.today_item = rumps.MenuItem("Today: loading...")
        self.today_item.set_callback(None)
        self.week_item = rumps.MenuItem("7 days: loading...")
        self.week_item.set_callback(None)
        self.month_item = rumps.MenuItem("30 days: loading...")
        self.month_item.set_callback(None)

        # Status / actions
        self.status_item = rumps.MenuItem("Status: starting...")
        self.status_item.set_callback(None)

        self.refresh_btn = rumps.MenuItem("Refresh Now", callback=self.manual_refresh)
        self.settings_btn = rumps.MenuItem("Settings...", callback=self.open_settings)
        self.quit_btn = rumps.MenuItem("Quit", callback=self.quit_app)

        self.menu = [
            self.title_item,
            None,
            self.rl_header,
            self.tok_limit_item,
            self.tok_remaining_item,
            self.tok_used_item,
            self.tok_reset_item,
            None,
            self.req_limit_item,
            self.req_remaining_item,
            self.req_reset_item,
            None,
            self.usage_header,
            self.today_item,
            self.week_item,
            self.month_item,
            None,
            self.status_item,
            self.refresh_btn,
            self.settings_btn,
            self.quit_btn,
        ]

        # Periodic refresh
        refresh_mins = self.config.get("refresh_minutes", 5)
        self.timer = rumps.Timer(self.refresh_data, refresh_mins * 60)
        self.timer.start()

        # Immediate first refresh
        threading.Thread(target=self._initial_refresh, daemon=True).start()

    def _initial_refresh(self):
        time.sleep(2)
        self.refresh_data(None)

    @rumps.timer(30)
    def tick_countdown(self, _):
        """Update reset countdowns every 30 seconds."""
        if self.last_probe:
            tok_reset = self.last_probe.get("tok_reset", "")
            req_reset = self.last_probe.get("req_reset", "")
            if tok_reset:
                self.tok_reset_item.title = f"Resets in: {time_until_reset(tok_reset)}"
            if req_reset:
                self.req_reset_item.title = f"Resets in: {time_until_reset(req_reset)}"

    def refresh_data(self, _):
        key = self.config.get("api_key", "")
        if not key:
            self.title = "⚠️ Key"
            self.status_item.title = "Status: No API key — open Settings"
            return

        model = self.config.get("model", "claude-haiku-4-5-20251001")

        try:
            probe = probe_rate_limits(key, model)
            self.last_probe = probe
            self.last_error = None

            # Log to SQLite
            log_usage(self.db, probe)

            # --- Update rate limit display ---
            tok_limit = probe.get("tok_limit")
            tok_remaining = probe.get("tok_remaining")
            req_limit = probe.get("req_limit")
            req_remaining = probe.get("req_remaining")

            if tok_limit is not None:
                tok_used = tok_limit - (tok_remaining or 0)
                pct = fmt_pct(tok_remaining, tok_limit)
                self.title = f"◉ {pct} used"
                self.tok_limit_item.title = f"Token limit: {fmt_tokens(tok_limit)}"
                self.tok_remaining_item.title = f"Remaining: {fmt_tokens(tok_remaining or 0)}"
                self.tok_used_item.title = f"Used: {fmt_tokens(tok_used)} ({pct})"
            else:
                self.title = "◉ —"
                self.tok_limit_item.title = "Token limit: unavailable"
                self.tok_remaining_item.title = "Remaining: unavailable"
                self.tok_used_item.title = "Used: unavailable"

            tok_reset = probe.get("tok_reset", "")
            self.tok_reset_item.title = f"Resets in: {time_until_reset(tok_reset)}"

            if req_limit is not None:
                req_used = req_limit - (req_remaining or 0)
                self.req_limit_item.title = f"Request limit: {req_limit:,}"
                self.req_remaining_item.title = f"Remaining: {req_remaining:,}"
                self.req_reset_item.title = f"Resets in: {time_until_reset(probe.get('req_reset', ''))}"
            else:
                self.req_limit_item.title = "Request limit: unavailable"
                self.req_remaining_item.title = "Remaining: unavailable"
                self.req_reset_item.title = "Resets in: unavailable"

            # --- Local usage history ---
            today = query_usage(self.db, 24)
            week = query_usage(self.db, 24 * 7)
            month = query_usage(self.db, 24 * 30)

            self.today_item.title = (
                f"Today: {fmt_tokens(today['input'] + today['output'])} "
                f"({today['calls']} calls)"
            )
            self.week_item.title = (
                f"7 days: {fmt_tokens(week['input'] + week['output'])} "
                f"({week['calls']} calls)"
            )
            self.month_item.title = (
                f"30 days: {fmt_tokens(month['input'] + month['output'])} "
                f"({month['calls']} calls)"
            )

            now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")
            self.status_item.title = f"Status: Updated at {now_str}"

        except requests.exceptions.HTTPError as e:
            self.last_error = str(e)
            status = getattr(e.response, "status_code", "?")
            self.title = "⚠️ Err"
            self.status_item.title = f"Status: HTTP {status}"
        except requests.exceptions.ConnectionError:
            self.title = "⚠️ Net"
            self.status_item.title = "Status: No connection"
        except Exception as e:
            self.last_error = str(e)
            self.title = "⚠️ Err"
            self.status_item.title = f"Status: {str(e)[:40]}"

    def manual_refresh(self, _):
        self.title = "⏳"
        self.status_item.title = "Status: Refreshing..."
        threading.Thread(target=self.refresh_data, args=(None,), daemon=True).start()

    def open_settings(self, _):
        resp = rumps.Window(
            title="Claude Token Tracker Settings",
            message="Enter your Anthropic API key (sk-ant-api...):",
            default_text=self.config.get("api_key", ""),
            ok="Save",
            cancel="Cancel",
            dimensions=(420, 24),
        ).run()

        if resp.clicked:
            key = resp.text.strip()
            if key:
                self.config["api_key"] = key
                save_config(self.config)
                rumps.notification(
                    "Claude Token Tracker",
                    "Settings saved",
                    "API key updated. Refreshing...",
                )
                self.manual_refresh(None)

    def quit_app(self, _):
        if self.db:
            self.db.close()
        rumps.quit_application()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    app = TokenTrackerApp()
    app.run()


if __name__ == "__main__":
    main()
