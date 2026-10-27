#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
# PostToolUse hook: one heartbeat line per tool call while a night shift is ACTIVE.
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
P="$ROOT/.agent-pipeline"
[ -f "$P/ACTIVE" ] || exit 0
tool=$(sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
line="$(date +%s) ${tool:-?}"
echo "$line" >> "$P/heartbeat.log"
echo "$line" > "$P/HEARTBEAT"
exit 0
