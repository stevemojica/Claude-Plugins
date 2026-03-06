#!/usr/bin/env python3
"""
Claude Token Usage Tracker — macOS Menu Bar App

Displays your Anthropic API token usage and cost in the macOS menu bar,
with a countdown to when your usage period resets.
"""

import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import rumps

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".claude-token-tracker"
CONFIG_FILE = CONFIG_DIR / "config.json"
ANTHROPIC_API_BASE = "https://api.anthropic.com/v1/organizations"
REFRESH_INTERVAL_SECONDS = 300  # 5 minutes


def load_config():
    """Load config from file, falling back to environment variables."""
    config = {
        "admin_api_key": os.environ.get("ANTHROPIC_ADMIN_KEY", ""),
        "refresh_minutes": 5,
        "billing_cycle_day": 1,  # day of month the billing cycle resets
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
# Anthropic Admin API helpers
# ---------------------------------------------------------------------------


def fetch_usage(admin_key: str, start: str, end: str, group_by: str = "model"):
    """Fetch token usage from the Anthropic Admin API."""
    url = f"{ANTHROPIC_API_BASE}/usage_report/messages"
    params = {
        "starting_at": start,
        "ending_at": end,
        "bucket_width": "1d",
        "group_by[]": group_by,
    }
    headers = {
        "x-api-key": admin_key,
        "anthropic-version": "2023-06-01",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_cost(admin_key: str, start: str, end: str):
    """Fetch cost data from the Anthropic Admin API."""
    url = f"{ANTHROPIC_API_BASE}/cost_report"
    params = {
        "starting_at": start,
        "ending_at": end,
        "group_by[]": "description",
    }
    headers = {
        "x-api-key": admin_key,
        "anthropic-version": "2023-06-01",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def fmt_tokens(n: int) -> str:
    """Format a token count in a human-friendly way."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def fmt_cost(cents: float) -> str:
    """Format cost in dollars from cents."""
    return f"${cents / 100:.2f}"


def billing_period(cycle_day: int):
    """Return (start, end, reset_dt) for the current billing cycle."""
    now = datetime.now(timezone.utc)
    # Find current period start
    try:
        period_start = now.replace(day=cycle_day, hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        # cycle_day doesn't exist in this month (e.g. 31 in Feb), use last day
        import calendar
        last_day = calendar.monthrange(now.year, now.month)[1]
        period_start = now.replace(day=min(cycle_day, last_day), hour=0, minute=0, second=0, microsecond=0)

    if period_start > now:
        # Haven't reached cycle day this month yet — period started last month
        if now.month == 1:
            period_start = period_start.replace(year=now.year - 1, month=12)
        else:
            import calendar
            prev_month = now.month - 1
            last_day = calendar.monthrange(now.year, prev_month)[1]
            period_start = period_start.replace(month=prev_month, day=min(cycle_day, last_day))

    # Period end / reset is next occurrence of cycle_day
    if now.month == 12:
        next_month = 1
        next_year = now.year + 1
    else:
        next_month = now.month + 1
        next_year = now.year
    import calendar
    last_day = calendar.monthrange(next_year, next_month)[1]
    reset_dt = datetime(next_year, next_month, min(cycle_day, last_day), tzinfo=timezone.utc)

    if reset_dt <= now:
        # Edge case: already past reset this month
        if next_month == 12:
            reset_dt = datetime(next_year + 1, 1, min(cycle_day, 31), tzinfo=timezone.utc)
        else:
            nm = next_month + 1
            ld = calendar.monthrange(next_year, nm)[1]
            reset_dt = datetime(next_year, nm, min(cycle_day, ld), tzinfo=timezone.utc)

    return (
        period_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        reset_dt,
    )


def time_until(dt: datetime) -> str:
    """Human-friendly countdown string."""
    now = datetime.now(timezone.utc)
    delta = dt - now
    if delta.total_seconds() <= 0:
        return "now"
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes = rem // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "<1m"


# ---------------------------------------------------------------------------
# Menu Bar App
# ---------------------------------------------------------------------------


class TokenTrackerApp(rumps.App):
    def __init__(self):
        super().__init__("⏳", quit_button=None)
        self.config = load_config()
        self.usage_data = {}
        self.cost_data = {}
        self.last_error = None
        self.reset_dt = None

        # --- Build menu ---
        self.title_item = rumps.MenuItem("Claude Token Tracker", callback=None)
        self.title_item.set_callback(None)

        self.separator1 = None  # rumps uses None for separators

        self.period_item = rumps.MenuItem("Period: loading...")
        self.period_item.set_callback(None)
        self.reset_item = rumps.MenuItem("Resets in: loading...")
        self.reset_item.set_callback(None)

        self.total_tokens_item = rumps.MenuItem("Tokens: loading...")
        self.total_tokens_item.set_callback(None)
        self.total_cost_item = rumps.MenuItem("Cost: loading...")
        self.total_cost_item.set_callback(None)

        self.breakdown_menu = rumps.MenuItem("Breakdown by Model")

        self.today_header = rumps.MenuItem("— Today —")
        self.today_header.set_callback(None)
        self.today_tokens_item = rumps.MenuItem("Today tokens: loading...")
        self.today_tokens_item.set_callback(None)

        self.status_item = rumps.MenuItem("Status: loading...")
        self.status_item.set_callback(None)

        self.refresh_btn = rumps.MenuItem("Refresh Now", callback=self.manual_refresh)
        self.settings_btn = rumps.MenuItem("Settings...", callback=self.open_settings)
        self.quit_btn = rumps.MenuItem("Quit", callback=self.quit_app)

        self.menu = [
            self.title_item,
            None,
            self.period_item,
            self.reset_item,
            None,
            self.total_tokens_item,
            self.total_cost_item,
            self.breakdown_menu,
            None,
            self.today_header,
            self.today_tokens_item,
            None,
            self.status_item,
            self.refresh_btn,
            self.settings_btn,
            self.quit_btn,
        ]

        # Start periodic refresh
        refresh_mins = self.config.get("refresh_minutes", 5)
        self.timer = rumps.Timer(self.refresh_data, refresh_mins * 60)
        self.timer.start()

        # Also do an immediate refresh in background
        threading.Thread(target=self._initial_refresh, daemon=True).start()

    def _initial_refresh(self):
        """Run first refresh after a short delay to let the app start."""
        time.sleep(2)
        self.refresh_data(None)

    def _update_reset_countdown(self, _):
        """Update the reset countdown in the menu (called by timer)."""
        if self.reset_dt:
            self.reset_item.title = f"Resets in: {time_until(self.reset_dt)}"

    @rumps.timer(60)
    def tick_countdown(self, _):
        """Update countdown every minute."""
        if self.reset_dt:
            self.reset_item.title = f"Resets in: {time_until(self.reset_dt)}"

    def refresh_data(self, _):
        """Fetch latest usage and cost data from the API."""
        key = self.config.get("admin_api_key", "")
        if not key:
            self.title = "⚠️ Key"
            self.status_item.title = "Status: No API key configured"
            self.last_error = "No admin API key"
            return

        cycle_day = self.config.get("billing_cycle_day", 1)
        start, end, reset_dt = billing_period(cycle_day)
        self.reset_dt = reset_dt

        # Today range
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        try:
            # Fetch billing-period usage (by model)
            usage = fetch_usage(key, start, end, group_by="model")
            self.usage_data = usage

            # Fetch today's usage
            today_usage = fetch_usage(key, today_start, end, group_by="model")

            # Fetch billing-period cost
            try:
                cost = fetch_cost(key, start, end)
                self.cost_data = cost
            except Exception:
                self.cost_data = {}

            self.last_error = None

            # --- Aggregate totals ---
            total_input = 0
            total_output = 0
            model_breakdown = {}

            for bucket in usage.get("data", []):
                inp = bucket.get("input_tokens", 0) + bucket.get("input_cached_tokens", 0)
                out = bucket.get("output_tokens", 0)
                total_input += inp
                total_output += out
                model = bucket.get("model", "unknown")
                if model not in model_breakdown:
                    model_breakdown[model] = {"input": 0, "output": 0}
                model_breakdown[model]["input"] += inp
                model_breakdown[model]["output"] += out

            total = total_input + total_output

            # Today totals
            today_total = 0
            for bucket in today_usage.get("data", []):
                today_total += (
                    bucket.get("input_tokens", 0)
                    + bucket.get("input_cached_tokens", 0)
                    + bucket.get("output_tokens", 0)
                )

            # Total cost
            total_cost_cents = 0.0
            for item in self.cost_data.get("data", []):
                total_cost_cents += float(item.get("cost_cents", 0))

            # --- Update UI ---
            self.title = f"◉ {fmt_tokens(total)}"
            self.period_item.title = f"Period: {start[:10]} → {end[:10]}"
            self.reset_item.title = f"Resets in: {time_until(reset_dt)}"
            self.total_tokens_item.title = (
                f"Tokens: {fmt_tokens(total)}  (↓{fmt_tokens(total_input)} ↑{fmt_tokens(total_output)})"
            )

            if total_cost_cents > 0:
                self.total_cost_item.title = f"Cost: {fmt_cost(total_cost_cents)}"
            else:
                self.total_cost_item.title = "Cost: —"

            self.today_tokens_item.title = f"Today: {fmt_tokens(today_total)} tokens"

            # Model breakdown
            self.breakdown_menu.clear()
            for model, counts in sorted(
                model_breakdown.items(),
                key=lambda x: x[1]["input"] + x[1]["output"],
                reverse=True,
            ):
                mtotal = counts["input"] + counts["output"]
                item = rumps.MenuItem(
                    f"{model}: {fmt_tokens(mtotal)}  (↓{fmt_tokens(counts['input'])} ↑{fmt_tokens(counts['output'])})"
                )
                item.set_callback(None)
                self.breakdown_menu[item.title] = item

            if not model_breakdown:
                no_data = rumps.MenuItem("No usage data yet")
                no_data.set_callback(None)
                self.breakdown_menu[no_data.title] = no_data

            now_str = now.strftime("%H:%M")
            self.status_item.title = f"Status: Updated at {now_str}"

        except requests.exceptions.HTTPError as e:
            self.last_error = str(e)
            self.title = "⚠️ Err"
            status = getattr(e.response, "status_code", "?")
            self.status_item.title = f"Status: HTTP {status} error"
        except requests.exceptions.ConnectionError:
            self.last_error = "Connection error"
            self.title = "⚠️ Net"
            self.status_item.title = "Status: Connection error"
        except Exception as e:
            self.last_error = str(e)
            self.title = "⚠️ Err"
            self.status_item.title = f"Status: {str(e)[:40]}"

    def manual_refresh(self, _):
        self.title = "⏳"
        self.status_item.title = "Status: Refreshing..."
        threading.Thread(target=self.refresh_data, args=(None,), daemon=True).start()

    def open_settings(self, _):
        """Open a settings dialog to configure the API key and preferences."""
        # Prompt for Admin API key
        resp = rumps.Window(
            title="Claude Token Tracker Settings",
            message="Enter your Anthropic Admin API key (sk-ant-admin...):",
            default_text=self.config.get("admin_api_key", ""),
            ok="Save",
            cancel="Cancel",
            dimensions=(420, 24),
        ).run()

        if resp.clicked:
            key = resp.text.strip()
            if key:
                self.config["admin_api_key"] = key
                save_config(self.config)
                rumps.notification(
                    "Claude Token Tracker",
                    "Settings saved",
                    "API key updated. Refreshing data...",
                )
                self.manual_refresh(None)

        # Prompt for billing cycle day
        resp2 = rumps.Window(
            title="Billing Cycle",
            message="Which day of the month does your billing cycle reset? (1-28)",
            default_text=str(self.config.get("billing_cycle_day", 1)),
            ok="Save",
            cancel="Cancel",
            dimensions=(200, 24),
        ).run()

        if resp2.clicked:
            try:
                day = int(resp2.text.strip())
                if 1 <= day <= 28:
                    self.config["billing_cycle_day"] = day
                    save_config(self.config)
            except ValueError:
                pass

    def quit_app(self, _):
        rumps.quit_application()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    app = TokenTrackerApp()
    app.run()


if __name__ == "__main__":
    main()
