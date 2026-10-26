#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
# One-liner: curl -fsSL https://raw.githubusercontent.com/jaylooloomi/i-want-to-sleep/main/install.sh | bash
# Limit to one repo:  curl -fsSL ... | SCOPE=local bash
set -e
command -v claude >/dev/null || { echo "claude CLI not found. Install Claude Code first."; exit 1; }
claude plugin marketplace add jaylooloomi/i-want-to-sleep 2>/dev/null || claude plugin marketplace update jaylooloomi
claude plugin install i-want-to-sleep@jaylooloomi ${SCOPE:+--scope "$SCOPE"}
claude plugin list | grep -A1 i-want-to-sleep || true
echo
echo "Installed. Now configure (one of):"
echo "  A. ~/.claude/settings.json -> \"env\": { \"CLAUDE_CODE_STOP_HOOK_BLOCK_CAP\": \"0\" }  (once)"
echo "  B. export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0  (per launch)"
echo "Then: claude --dangerously-skip-permissions  and type /i-want-to-sleep:sleep 8"
