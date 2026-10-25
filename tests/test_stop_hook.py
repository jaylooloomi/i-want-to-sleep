#!/usr/bin/env python3
"""Run: python3 tests/test_stop_hook.py — every Stop-hook path must exit 0 (allow) or 2 (block), never crash."""
import os, subprocess, sys, tempfile, time
here = os.path.dirname(os.path.abspath(__file__))
hook = os.path.join(here, '..', 'plugins', 'i-want-to-sleep', 'scripts', 'night-shift-stop.sh')
bad = 0
def case(name, files, exp, contains=None):
    global bad
    root = tempfile.mkdtemp(); P = os.path.join(root, '.agent-pipeline'); os.makedirs(P)
    for k, v in files.items(): open(os.path.join(P, k), 'w').write(v)
    r = subprocess.run([hook], capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
    ok = r.returncode == exp and (contains is None or contains in r.stderr)
    if not ok: bad += 1; print(f"FAIL {name}: exit {r.returncode} (want {exp}) stderr={r.stderr[:120]!r}")
now = int(time.time())
case('daytime, no ACTIVE', {}, 0)
case('DONE present', {'ACTIVE': '', 'DONE': ''}, 0)
case('running', {'ACTIVE': '', 'DEADLINE': str(now + 3600)}, 2, '夜班進行中')
case('deadline passed, BASE file', {'ACTIVE': '', 'DEADLINE': str(now - 5), 'BASE': 'dev'}, 2, 'BASE=dev')
case('deadline passed, no BASE file', {'ACTIVE': '', 'DEADLINE': str(now - 5)}, 2, 'BASE=main')
case('turn limit', {'ACTIVE': '', 'DEADLINE': str(now + 3600), 'turns': '999'}, 2, '結束條件')
case('user STOP', {'ACTIVE': '', 'DEADLINE': str(now + 3600), 'STOP': ''}, 2, '使用者喊停')
case('already asked to finish', {'ACTIVE': '', 'DEADLINE': str(now - 5), 'STATE': 'finishing'}, 0)
case('no DEADLINE → created', {'ACTIVE': ''}, 2, '夜班進行中')
print(f"{9-bad}/9 passed"); sys.exit(1 if bad else 0)
