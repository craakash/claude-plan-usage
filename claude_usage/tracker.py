"""Core logic for fetching Claude plan usage limits from the API."""

import json
import subprocess
from datetime import datetime, timezone


# ANSI color codes
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
BLUE = "\033[38;5;27m"
GRAY = "\033[38;5;245m"
WHITE = "\033[97m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"


def _get_oauth_token():
    """Read the OAuth access token from macOS Keychain."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-g"],
            capture_output=True, text=True
        )
        for line in result.stderr.splitlines():
            if line.startswith("password:"):
                raw = line.split("password: ", 1)[1].strip().strip('"')
                creds = json.loads(raw)
                return creds.get("claudeAiOauth", {}).get("accessToken")
    except Exception:
        pass
    return None


def _fetch_rate_limits(token):
    """Make a minimal API call and parse rate limit headers from the response."""
    try:
        result = subprocess.run(
            [
                "curl", "-s", "-D-",
                "-H", f"Authorization: Bearer {token}",
                "-H", "anthropic-version: 2023-06-01",
                "-H", "content-type: application/json",
                "-d", '{"model":"claude-haiku-4-5-20251001","max_tokens":1,"messages":[{"role":"user","content":"1"}]}',
                "https://api.anthropic.com/v1/messages"
            ],
            capture_output=True, text=True, timeout=15
        )
        headers = {}
        for line in result.stdout.splitlines():
            if line.startswith("anthropic-ratelimit"):
                key, _, value = line.partition(": ")
                headers[key.strip()] = value.strip()
        return headers
    except Exception as e:
        return {"error": str(e)}


def _parse_limits(headers):
    """Parse rate limit headers into structured data."""
    limits = {}

    # 5-hour window (= "Current session" in the UI)
    if "anthropic-ratelimit-unified-5h-utilization" in headers:
        utilization = float(headers["anthropic-ratelimit-unified-5h-utilization"])
        reset_ts = int(headers.get("anthropic-ratelimit-unified-5h-reset", 0))
        reset_dt = datetime.fromtimestamp(reset_ts, tz=timezone.utc) if reset_ts else None
        limits["session"] = {
            "utilization": utilization,
            "percent": round(utilization * 100),
            "reset_ts": reset_ts,
            "reset_dt": reset_dt,
            "status": headers.get("anthropic-ratelimit-unified-5h-status", "unknown"),
        }

    # 7-day window (= "Weekly limits" in the UI)
    if "anthropic-ratelimit-unified-7d-utilization" in headers:
        utilization = float(headers["anthropic-ratelimit-unified-7d-utilization"])
        reset_ts = int(headers.get("anthropic-ratelimit-unified-7d-reset", 0))
        reset_dt = datetime.fromtimestamp(reset_ts, tz=timezone.utc) if reset_ts else None
        limits["weekly"] = {
            "utilization": utilization,
            "percent": round(utilization * 100),
            "reset_ts": reset_ts,
            "reset_dt": reset_dt,
            "status": headers.get("anthropic-ratelimit-unified-7d-status", "unknown"),
        }

    # Overall status
    limits["status"] = headers.get("anthropic-ratelimit-unified-status", "unknown")
    limits["representative_claim"] = headers.get("anthropic-ratelimit-unified-representative-claim", "")

    return limits


def _format_time_remaining(reset_dt):
    """Format the time remaining until reset as 'X hr Y min'."""
    if not reset_dt:
        return "unknown"
    now = datetime.now(tz=timezone.utc)
    delta = reset_dt - now
    total_seconds = max(0, int(delta.total_seconds()))
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    if hours > 0:
        return f"{hours} hr {minutes} min"
    return f"{minutes} min"


def _progress_bar(percent, width=40):
    """Render a terminal progress bar with color."""
    filled = int(width * percent / 100)
    if filled == 0 and percent > 0:
        filled = 1

    if percent >= 80:
        color = RED
    elif percent >= 50:
        color = YELLOW
    else:
        color = BLUE

    bar = color + "━" * filled + RESET + GRAY + "━" * (width - filled) + RESET
    return bar


def get_plan_limits():
    """Fetch and return the current plan usage limits."""
    token = _get_oauth_token()
    if not token:
        return None, "Could not find Claude Code OAuth token in Keychain."

    headers = _fetch_rate_limits(token)
    if "error" in headers:
        return None, f"API request failed: {headers['error']}"

    if not any("utilization" in k for k in headers):
        return None, "No rate limit data in API response. You may be rate-limited — try again in a minute."

    return _parse_limits(headers), None


def print_usage(**kwargs):
    """Print the plan usage limits in a style matching the Claude.ai settings page."""
    limits, error = get_plan_limits()

    if error:
        print(f"\n  {RED}Error:{RESET} {error}\n")
        return

    # Determine plan type from credentials
    token_info = ""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-g"],
            capture_output=True, text=True
        )
        for line in result.stderr.splitlines():
            if line.startswith("password:"):
                raw = line.split("password: ", 1)[1].strip().strip('"')
                creds = json.loads(raw)
                sub = creds.get("claudeAiOauth", {}).get("subscriptionType", "")
                if sub:
                    token_info = sub.capitalize()
    except Exception:
        pass

    plan_label = token_info if token_info else "Pro"
    bar_width = 40

    print()
    print(f"  {BOLD}Plan usage limits{RESET}  {DIM}{plan_label}{RESET}")
    print()

    # Current session (5h window)
    if "session" in limits:
        s = limits["session"]
        pct = s["percent"]
        time_left = _format_time_remaining(s["reset_dt"])
        print(f"  {BOLD}Current session{RESET}")
        print(f"  {DIM}Resets in {time_left}{RESET}")
        print(f"  {_progress_bar(pct, bar_width)}  {WHITE}{pct}% used{RESET}")
        print()

    # Weekly limits heading
    print(f"  {BOLD}Weekly limits{RESET}")
    print()

    # All models (7d window)
    if "weekly" in limits:
        w = limits["weekly"]
        pct = w["percent"]
        time_left = _format_time_remaining(w["reset_dt"])
        print(f"  {BOLD}All models{RESET}")
        print(f"  {DIM}Resets in {time_left}{RESET}")
        print(f"  {_progress_bar(pct, bar_width)}  {WHITE}{pct}% used{RESET}")
        print()

    # Status indicator
    status = limits.get("status", "unknown")
    if status == "allowed":
        status_icon = f"{GREEN}●{RESET}"
        status_text = "within limits"
    elif status == "throttled":
        status_icon = f"{YELLOW}●{RESET}"
        status_text = "throttled"
    else:
        status_icon = f"{RED}●{RESET}"
        status_text = status

    now_str = datetime.now().strftime("%H:%M:%S")
    print(f"  {DIM}Last updated: {now_str}{RESET}  {status_icon} {DIM}{status_text}{RESET}")
    print()
