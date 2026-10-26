#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
# PreToolUse(Write|Edit|MultiEdit|apply_patch) guard — logic in guard_write.py (Claude file_path + Codex apply_patch).
exec python3 "$(dirname "$0")/guard_write.py"
