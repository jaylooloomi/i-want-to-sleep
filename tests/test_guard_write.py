#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
"""Run: python3 tests/test_guard_write.py — covers Claude file_path, Codex apply_patch, and git-root fallback."""
import json, os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__))
guard = os.path.join(here, '..', 'plugins', 'i-want-to-sleep', 'scripts', 'guard-write.sh')
root = tempfile.mkdtemp(); os.makedirs(os.path.join(root, '.agent-pipeline')); open(os.path.join(root, '.agent-pipeline', 'ACTIVE'), 'w').close()
def patch(*hdrs): return "*** Begin Patch\n" + "\n".join(hdrs) + "\n@@\n-a\n+b\n*** End Patch\n"
CASES = [
 (0, {"file_path": "/r/src/Foo.cs"}), (2, {"file_path": "/r/appsettings.Development.json"}),
 (2, {"file_path": "/r/.gitlab-ci.yml"}), (2, {"file_path": "/r/Migrations/001.cs"}),
 (2, {"file_path": "/r/Web.csproj"}), (2, {"file_path": "/r/package.json"}), (0, {"file_path": "/r/src/package.jsonx"}),
 (0, {"command": patch("*** Update File: src/app.js")}),
 (2, {"command": patch("*** Update File: package.json")}),
 (2, {"command": patch("*** Add File: db/migrations/002_add.sql")}),
 (2, {"command": patch("*** Update File: src/app.js", "*** Update File: .env.local")}),
 (2, {"command": patch("*** Update File: src/old.js", "*** Move to: .github/workflows/ci.yml")}),
 (0, {"command": patch("*** Add File: docs/notes.md")}),
]
bad = 0
env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
for exp, ti in CASES:
    r = subprocess.run([guard], input=json.dumps({"tool_input": ti}), capture_output=True, text=True, env=env)
    if r.returncode != exp: bad += 1; print(f"FAIL expected {exp} got {r.returncode}: {ti}")
# git-root fallback (Codex does not set CLAUDE_PROJECT_DIR; may start in a subdirectory)
subprocess.run(['git', 'init', '-q', root]); sub = os.path.join(root, 'src', 'deep'); os.makedirs(sub)
env2 = {k: v for k, v in os.environ.items() if k != 'CLAUDE_PROJECT_DIR'}
r = subprocess.run([guard], input=json.dumps({"tool_input": {"file_path": "package.json"}}), capture_output=True, text=True, env=env2, cwd=sub)
if r.returncode != 2: bad += 1; print("FAIL git-root fallback from subdirectory")
log = os.path.join(root, '.agent-pipeline', 'blocked.log')
want = sum(1 for e, _ in CASES if e == 2) + 1   # +1 for the git-root fallback case
got = len(open(log, encoding='utf-8').read().splitlines()) if os.path.exists(log) else 0
if got != want: bad += 1; print(f"FAIL blocked.log has {got} lines, want {want}")
total = len(CASES) + 2
print(f"{total-bad}/{total} passed"); sys.exit(1 if bad else 0)
