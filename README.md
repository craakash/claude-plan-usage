# 🎯 claude-plan-usage

[![PyPI Version](https://img.shields.io/pypi/v/claude-plan-usage.svg)](https://pypi.org/project/claude-plan-usage/)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](#)

> **Your Claude plan usage limits — in the terminal.** No more switching to the desktop app.

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

---

## 📑 Table of Contents

- [✨ Key Features](#-key-features)
- [🤔 Why Not Other Tools?](#-why-not-other-tools)
- [🚀 Installation](#-installation)
- [📖 Usage](#-usage)
  - [Terminal](#terminal)
  - [Inside Claude Code (Slash Command)](#-inside-claude-code-slash-command)
  - [Python API](#-python-api)
- [🔍 How It Works](#-how-it-works)
- [🎨 Progress Bar Colors](#-progress-bar-colors)
- [📋 Requirements](#-requirements)
- [⚠️ Limitations](#️-limitations)
- [📝 License](#-license)

---

## ✨ Key Features

- **🎯 Exact numbers** — reads the same data as `claude.ai/settings/usage`, not estimates
- **⚡ Instant** — one command, results in 2 seconds
- **🔌 Claude Code integration** — add as a `/usage` slash command, never leave your session
- **🪶 Zero dependencies** — just Python standard library, nothing to install
- **🔑 Zero config** — auto-reads your auth from macOS Keychain
- **💰 Basically free** — each check costs ~$0.000001 (one Haiku token)
- **📊 Color-coded progress bars** — blue, yellow, red based on utilization

---

## 🤔 Why Not Other Tools?

Other usage trackers (like `claude-monitor`) parse your local session files and **estimate** your limits using token counts, ML predictions, and P90 calculations. They're guessing.

`claude-plan-usage` doesn't guess. It reads **undocumented rate limit headers** directly from Anthropic's API — the **exact same data source** that powers the `claude.ai/settings/usage` page.

When the dashboard says 50%, this tool says 50%. Same number. Same source.

| | 🔮 Other tools | 🎯 claude-plan-usage |
|---|---|---|
| **Data source** | Local session files | ✅ Live API response headers |
| **Accuracy** | Estimated from token counts | ✅ **Exact** — same as claude.ai dashboard |
| **What it shows** | Token counts, burn rates, predictions | ✅ **Actual plan utilization %** and reset times |
| **Setup** | Config files, plan selection, themes | ✅ `pip install` and done |
| **Dependencies** | Heavy (ML, Rich, Pydantic, Sentry) | ✅ **Zero** — Python standard library only |
| **Complexity** | 100+ files | ✅ ~200 lines of code |

> 💡 **The key discovery:** Anthropic returns `anthropic-ratelimit-unified-5h-utilization` and `anthropic-ratelimit-unified-7d-utilization` headers on every API response. These are undocumented. Nobody was reading them. Now you can.

---

## 🚀 Installation

```bash
pip install claude-plan-usage
```

That's it. No config. No setup. No API keys needed.

---

## 📖 Usage

### Terminal

```bash
claude-plan-usage
```

### 🔌 Inside Claude Code (Slash Command)

This is the cool part — you can check your usage **without leaving your Claude Code session**.

Create this file at `~/.claude/skills/usage/SKILL.md`:

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

Now just type `/usage` in any Claude Code session. ✨

### 🐍 Python API

```python
from claude_usage import get_plan_limits

limits, error = get_plan_limits()
if limits:
    print(f"Session: {limits['session']['percent']}% used")
    print(f"Weekly:  {limits['weekly']['percent']}% used")
    print(f"Status:  {limits['status']}")
```

---

## 🔍 How It Works

Anthropic returns **undocumented rate limit headers** on every API response:

| Header | What it tells you |
|---|---|
| `anthropic-ratelimit-unified-5h-utilization` | 📊 Current session usage (0.0 to 1.0) |
| `anthropic-ratelimit-unified-5h-reset` | ⏰ When the session resets (unix timestamp) |
| `anthropic-ratelimit-unified-7d-utilization` | 📊 Weekly usage (0.0 to 1.0) |
| `anthropic-ratelimit-unified-7d-reset` | ⏰ When the week resets (unix timestamp) |
| `anthropic-ratelimit-unified-status` | ✅ `allowed` or 🚫 `throttled` |

**How it works under the hood:**

1. 🔑 Reads your OAuth token from macOS Keychain (stored by Claude Code CLI on login)
2. 📡 Sends one tiny Haiku API call (1 token)
3. 📋 Reads the rate limit headers from the response
4. 🎨 Renders progress bars with colors in your terminal

Zero config. Zero dependencies. Just works.

---

## 🎨 Progress Bar Colors

| Color | Utilization | Vibe |
|---|---|---|
| 🔵 Blue | 0–49% | You're chilling |
| 🟡 Yellow | 50–79% | Maybe slow down |
| 🔴 Red | 80–100% | You're about to hit the wall |

---

## 📋 Requirements

| Requirement | Details |
|---|---|
| 🍎 **OS** | macOS (uses Keychain for auth) |
| 🤖 **Claude Code** | Installed and logged in |
| 🐍 **Python** | 3.9+ |

> 🐧 **Linux/Windows users:** PRs welcome! The main blocker is reading the OAuth token — everything else is cross-platform.

---

## ⚠️ Limitations

- **macOS only** for now — the OAuth token lives in macOS Keychain. Happy to accept PRs for other platforms.
- **Undocumented API headers** — Anthropic could change these anytime. If it breaks, [open an issue](https://github.com/craakash/claude-plan-usage/issues).

---

## 📝 License

MIT

---

**Built by [@craakash](https://github.com/craakash)** — because checking usage shouldn't require opening another app.
