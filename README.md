# claude-plan-usage

I got tired of switching to the Claude desktop app every time I wanted to check how much of my plan I'd burned through. Seriously, why isn't this just a terminal command? So I built one.

One command. That's it. No browser, no desktop app, no clicking through settings.

```
  Plan usage limits  Team

  Current session
  Resets in 4 hr 38 min
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  13% used

  Weekly limits

  All models
  Resets in 130 hr 58 min
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  4% used

  Last updated: 14:01:55  ● within limits
```

Everything you see on `claude.ai/settings/usage` — session limits, weekly limits, reset timers, utilization — now lives in your terminal.

## Install

```bash
pip install claude-plan-usage
```

## Usage

### From any terminal

```bash
claude-plan-usage
```

### Inside Claude Code (the cool part)

You can add this as a `/usage` slash command so you never leave your Claude Code session.

Create `~/.claude/skills/usage/SKILL.md`:

```markdown
---
name: usage
description: Show Claude plan usage limits (current session and weekly)
disable-model-invocation: true
allowed-tools: Bash
---

Run the following command and display the output to the user exactly as-is:

\```bash
claude-plan-usage
\```
```

Now just type `/usage` in any Claude Code session. Check your limits without leaving the conversation.

### Python API

```python
from claude_usage import get_plan_limits

limits, error = get_plan_limits()
if limits:
    print(f"Session: {limits['session']['percent']}% used")
    print(f"Weekly:  {limits['weekly']['percent']}% used")
```

## How it works

I discovered that Anthropic returns **undocumented rate limit headers** on every API response:

| Header | What it tells you |
|---|---|
| `anthropic-ratelimit-unified-5h-utilization` | Current session usage (0.0 to 1.0) |
| `anthropic-ratelimit-unified-5h-reset` | When the session resets (unix timestamp) |
| `anthropic-ratelimit-unified-7d-utilization` | Weekly usage (0.0 to 1.0) |
| `anthropic-ratelimit-unified-7d-reset` | When the week resets (unix timestamp) |
| `anthropic-ratelimit-unified-status` | `allowed` or `throttled` |

`claude-plan-usage` sends one tiny Haiku call (1 token, costs ~$0.000001), reads these headers, and renders the progress bars. Auth token is pulled from macOS Keychain where Claude Code stores it on login. Zero config needed.

## Progress bar colors

| Color | Utilization |
|---|---|
| Blue | 0–49% |
| Yellow | 50–79% |
| Red | 80–100% |

## Requirements

- **macOS** (auth is read from macOS Keychain — Linux/Windows PRs welcome)
- **Claude Code CLI** installed and logged in
- **Python 3.9+**

## Limitations

- macOS only for now. The OAuth token lives in macOS Keychain. Happy to accept PRs for other platforms.
- Uses undocumented Anthropic API headers. They could change anytime — if it breaks, open an issue.

## License

MIT
