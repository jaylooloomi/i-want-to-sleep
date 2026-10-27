#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
"""Write .agent-pipeline/END and TIMING: start, end, run time, early finish, last heartbeat, longest silence."""
import os, sys, time
P = os.path.join(sys.argv[1] if len(sys.argv) > 1 else os.getcwd(), '.agent-pipeline')
rd = lambda n, d=None: (open(os.path.join(P, n)).read().strip() if os.path.exists(os.path.join(P, n)) else d)
f = lambda t: time.strftime('%Y-%m-%d %H:%M', time.localtime(t))
h = lambda x: f'{x // 3600}h{x % 3600 // 60:02d}m'
e = int(time.time()); s = int(rd('START', e)); d = int(rd('DEADLINE', e))
beats = []
for line in (rd('heartbeat.log', '') or '').splitlines():
    try: t, tool = line.split(' ', 1); beats.append((int(t), tool))
    except ValueError: pass
parts = [f'開始 {f(s)}', f'結束 {f(e)}', f'實際執行 {h(e - s)}／預定 {h(d - s)}']
if d - e > 60: parts.append(f'提早 {h(d - e)} 收工')
if beats:
    parts.append(f'最後心跳 {f(beats[-1][0])}（{beats[-1][1]}）')
    times = [s] + [t for t, _ in beats] + [e]
    gap, at = max(((b - a, a) for a, b in zip(times, times[1:])), default=(0, s))
    parts.append(f'最長無動作 {h(gap)}（{f(at)} 起）' + ('　⚠️ 可能休眠或卡住' if gap > 1800 else ''))
else:
    parts.append('無心跳紀錄')
open(os.path.join(P, 'END'), 'w').write(str(e))
open(os.path.join(P, 'TIMING'), 'w', encoding='utf-8').write('｜'.join(parts) + '\n')
print('｜'.join(parts))
