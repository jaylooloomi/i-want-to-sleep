#!/usr/bin/env bash
# PreToolUse(Write|Edit|MultiEdit|apply_patch) guard — logic in guard_write.py (Claude file_path + Codex apply_patch).
exec python3 "$(dirname "$0")/guard_write.py"
