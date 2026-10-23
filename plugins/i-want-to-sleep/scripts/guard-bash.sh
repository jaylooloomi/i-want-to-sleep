#!/usr/bin/env bash
# PreToolUse(Bash) guard — logic lives in guard_bash.py (parses segments, ignores heredoc bodies & quoted text).
exec python3 "$(dirname "$0")/guard_bash.py"
