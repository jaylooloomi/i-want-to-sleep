#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
"""PreToolUse(Bash) guard for night shifts.

Checks only what will actually execute: heredoc bodies and quoted strings are
ignored, and each rule looks at the command words it is about (git, rm, npm …)
rather than the whole command line. Falls back to whole-string matching only
when the command cannot be parsed.
Exit 2 + stderr = block. Exit 0 = allow.
"""
import json, os, re, shlex, subprocess, sys

PROTECTED = re.compile(
    r'(\.gitlab-ci\.yml|\.github/workflows|(^|/)[Mm]igrations?/|appsettings[^/\s]*\.json'
    r'|(^|/)\.env|web\.config|app\.config|\.csproj$|(^|/)package\.json$|requirements[^/\s]*\.txt'
    r'|Directory\.Packages\.props)')

ROOT = None
CMD = ''

def log_block(root, rule, detail):
    """Append every blocked attempt to .agent-pipeline/blocked.log — written by the hook, not the model."""
    try:
        import datetime
        line = detail.replace('\n', ' ⏎ ')[:300]
        with open(os.path.join(root, '.agent-pipeline', 'blocked.log'), 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{rule}\t{line}\n")
    except Exception:
        pass

def deny(msg):
    if ROOT: log_block(ROOT, msg, CMD)
    sys.stderr.write(f"夜班防線阻擋：{msg}。夜班不允許此動作；改用其他方式，或記錄到 result.md「需要你決定的事」。\n")
    sys.exit(2)

def strip_heredocs(cmd):
    out, lines, i = [], cmd.split('\n'), 0
    while i < len(lines):
        line = lines[i]; out.append(line)
        m = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        if m:
            tag = m.group(2); i += 1
            while i < len(lines) and lines[i].strip() != tag:
                i += 1
        i += 1
    return '\n'.join(out)

def segments(cmd):
    lex = shlex.shlex(strip_heredocs(cmd), posix=True, punctuation_chars=';&|<>()')
    lex.whitespace_split = True
    lex.commenters = ''
    seg = []
    for tok in lex:
        if tok in (';', '&&', '||', '|', '&', '(', ')', '\n') or set(tok) <= set(';&|()'):
            if seg: yield seg
            seg = []
        else:
            seg.append(tok)
    if seg: yield seg

def unwrap(seg):
    # drop env assignments and wrappers: FOO=1 sudo env time nohup …
    while seg and (re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', seg[0]) or seg[0] in ('sudo', 'env', 'time', 'nohup', 'command', 'exec')):
        seg = seg[1:]
    return seg

def git_sub(seg):
    i = 1
    while i < len(seg) and seg[i].startswith('-'):
        i += 2 if seg[i] in ('-C', '-c') else 1
    return (seg[i], seg[i + 1:]) if i < len(seg) else (None, [])

def check_segment(seg):
    seg = unwrap(seg)
    if not seg: return
    w = os.path.basename(seg[0])

    if w == 'git':
        sub, args = git_sub(seg)
        if sub == 'push':
            flags = [a for a in args if a.startswith('-')]
            pos = [a for a in args if not a.startswith('-')]
            if any(f in ('--force', '-f', '--force-with-lease', '--delete', '-d', '--mirror', '--all', '--tags') or f.startswith('--force') for f in flags):
                deny("git push 帶 force/delete/mirror")
            if len(pos) != 2 or ':' in pos[1] or not pos[1].startswith('night-shift/'):
                deny("git push 只允許 `git push [-u] <remote> night-shift/<…>`")
        elif sub in ('merge', 'rebase'):
            deny(f"git {sub}")
        elif sub == 'reset' and '--hard' in args:
            deny("git reset --hard")
        elif sub in ('checkout', 'switch') and args and args[-1] in ('main', 'master', 'develop') and not any(a in ('-b', '-c', '--create') for a in args):
            deny("切換到主分支")

    elif w == 'rm':
        flags = ''.join(a[1:] for a in seg[1:] if a.startswith('-') and not a.startswith('--'))
        if ('r' in flags or 'R' in flags or '--recursive' in seg) and ('f' in flags or '--force' in seg):
            deny("rm -rf")

    elif (w == 'dotnet' and seg[1:3] == ['add', 'package']) \
      or (w in ('npm', 'pnpm', 'yarn', 'bun') and len(seg) > 2 and seg[1] in ('install', 'i', 'add') and any(not a.startswith('-') for a in seg[2:])) \
      or (w in ('pip', 'pip3') and len(seg) > 1 and seg[1] == 'install') \
      or (w == 'nuget' and len(seg) > 1 and seg[1] == 'install'):
        deny("新增第三方套件")

    targets = []
    if w == 'sed' and any(a == '-i' or a.startswith('-i') for a in seg[1:]):
        targets = [a for a in seg[1:] if not a.startswith('-')][1:]
    elif w in ('tee', 'mv', 'cp', 'truncate'):
        targets = [a for a in seg[1:] if not a.startswith('-')]
        if w in ('mv', 'cp'): targets = targets[-1:]
    for i, a in enumerate(seg):
        if a in ('>', '>>') and i + 1 < len(seg):
            targets.append(seg[i + 1])
    for t in targets:
        if PROTECTED.search(t):
            deny(f"透過 shell 修改禁改清單中的檔案（{t}）")

def fallback(cmd):
    # unparseable → conservative whole-string check (old behaviour)
    if re.search(r'git\s+push', cmd) and not re.search(r'git\s+push(\s+(-u|--set-upstream))?\s+[\w.-]+\s+night-shift/[\w./-]+\s*$', cmd):
        deny("git push（命令無法解析，保守阻擋）")
    if re.search(r'git\s+(merge|rebase)|reset\s+--hard|rm\s+-[A-Za-z]*(rf|fr)', cmd):
        deny("危險指令（命令無法解析，保守阻擋）")

def main():
    root = os.environ.get('CLAUDE_PROJECT_DIR')
    if not root:
        try:
            root = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            root = ''
    root = root or os.getcwd()
    if not os.path.isfile(os.path.join(root, '.agent-pipeline', 'ACTIVE')):
        return
    try:
        cmd = json.load(sys.stdin).get('tool_input', {}).get('command', '')
    except Exception:
        return
    if not cmd: return
    global ROOT, CMD
    ROOT, CMD = root, cmd
    try:
        segs = list(segments(cmd))
    except ValueError:
        fallback(cmd); return
    for s in segs:
        check_segment(s)

if __name__ == '__main__':
    main()
