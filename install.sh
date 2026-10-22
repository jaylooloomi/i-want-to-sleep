#!/usr/bin/env bash
# One-liner: curl -fsSL https://raw.githubusercontent.com/jaylooloomi/i-want-to-sleep/main/install.sh | bash
set -e
command -v claude >/dev/null || { echo "claude CLI not found. Install Claude Code first."; exit 1; }
claude plugin marketplace add jaylooloomi/i-want-to-sleep 2>/dev/null || claude plugin marketplace update jaylooloomi
claude plugin install i-want-to-sleep@jaylooloomi
claude plugin list | grep -A1 i-want-to-sleep || true
echo
echo "Installed. Before the first night: export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0 and start with --dangerously-skip-permissions (see README > Before each night)."
