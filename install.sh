#!/usr/bin/env bash
# 一行安裝：curl -fsSL https://raw.githubusercontent.com/jaylooloomi/i-want-to-sleep/main/install.sh | bash
set -e
command -v claude >/dev/null || { echo "找不到 claude CLI，請先安裝 Claude Code"; exit 1; }
claude plugin marketplace add jaylooloomi/i-want-to-sleep 2>/dev/null || claude plugin marketplace update i-want-to-sleep
claude plugin install i-want-to-sleep@i-want-to-sleep
claude plugin list | grep -A1 i-want-to-sleep || true
echo
echo "安裝完成。使用前請看 README「每晚啟動前」：export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0，並用 --dangerously-skip-permissions 啟動。"
