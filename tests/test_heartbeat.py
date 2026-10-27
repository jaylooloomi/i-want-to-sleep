#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
"""Run: python3 tests/test_heartbeat.py — heartbeat hook, timing.py (last heartbeat / longest silence), nightshift INCOMPLETE marker."""
import json, os, stat, subprocess, sys, tempfile, time
here = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(here, '..', 'plugins', 'i-want-to-sleep', 'scripts')
bad = []
r = tempfile.mkdtemp(); P = os.path.join(r, '.agent-pipeline'); os.makedirs(P); env = dict(os.environ, CLAUDE_PROJECT_DIR=r)
hb = lambda tool: subprocess.run([os.path.join(S, 'heartbeat.sh')], input=json.dumps({"tool_name": tool, "tool_input": {}}), text=True, env=env)
hb('Bash')
if os.path.exists(os.path.join(P, 'heartbeat.log')): bad.append('heartbeat written without ACTIVE')
open(os.path.join(P, 'ACTIVE'), 'w').close(); hb('Bash'); hb('Edit')
log = open(os.path.join(P, 'heartbeat.log')).read().split('\n')
if len([l for l in log if l]) != 2 or not log[1].endswith('Edit'): bad.append(f'heartbeat.log content {log!r}')
now = int(time.time())
open(os.path.join(P, 'START'), 'w').write(str(now - 3 * 3600)); open(os.path.join(P, 'DEADLINE'), 'w').write(str(now + 5 * 3600))
open(os.path.join(P, 'heartbeat.log'), 'w').write(f"{now - 3*3600 + 60} Bash\n{now - 3*3600 + 120} Edit\n{now - 600} Bash\n")
out = subprocess.run([sys.executable, os.path.join(S, 'timing.py'), r], capture_output=True, text=True).stdout
for want in ('最後心跳', '最長無動作 2h', '可能休眠或卡住', '提早 5h'):
    if want not in out: bad.append(f'timing missing {want!r}: {out}')
# launcher: agent exits without wrap-up → INCOMPLETE.md
fake = tempfile.mkdtemp(); fc = os.path.join(fake, 'claude'); open(fc, 'w').write('#!/bin/sh\nexit 0\n'); os.chmod(fc, 0o755)
subprocess.run(['git', 'init', '-q', r])
subprocess.run([os.path.join(here, '..', 'bin', 'nightshift')], cwd=r, env=dict(os.environ, PATH=fake + ':' + os.environ['PATH']), capture_output=True)
inc = os.path.join(P, 'INCOMPLETE.md')
if not os.path.exists(inc) or 'Last heartbeat' not in open(inc).read(): bad.append('INCOMPLETE.md not written')
os.remove(inc); open(os.path.join(P, 'DONE'), 'w').close()
subprocess.run([os.path.join(here, '..', 'bin', 'nightshift')], cwd=r, env=dict(os.environ, PATH=fake + ':' + os.environ['PATH']), capture_output=True)
if os.path.exists(inc): bad.append('INCOMPLETE.md written although DONE')
for b in bad: print('FAIL', b)
print(f"{6 - len(bad)}/6 passed"); sys.exit(1 if bad else 0)
