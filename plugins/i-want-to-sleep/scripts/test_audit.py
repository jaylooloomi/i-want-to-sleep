#!/usr/bin/env python3
"""Static audit of test changes since the night shift started (BASE..HEAD).

Written by the Stop hook, not the model, to .agent-pipeline/test-audit.md.
Flags: deleted test files, removed test cases, newly skipped tests, net-removed assertions.
"""
import os, re, subprocess, sys

TEST_PATH = re.compile(r'(^|/)(tests?|spec|__tests__)(/|$)|(_test|\.test|\.spec|Tests?)\.[A-Za-z]+$|(^|/)test_[^/]+$', re.I)
CASE = re.compile(r'^\s*(async\s+)?def\s+test\w*|^\s*(it|test|describe)\s*\(|^\s*\[(Test|Fact|Theory|TestMethod)\]|^\s*@Test\b|^\s*func\s+test|^\s*func\s+Test\w+\(')
SKIP = re.compile(r'@pytest\.mark\.(skip|xfail)|pytest\.skip\(|\b(it|describe|test)\.skip\(|\bxit\(|\bxdescribe\(|\[Ignore|\[Skip|@Disabled|@Ignore|t\.Skip\(|\bpending\(|skip_test|@unittest\.skip', re.I)
ASSERT = re.compile(r'\bassert|\bexpect\s*\(|\bAssert\.|\bshould\b|\bt\.(Error|Fatal)|\bassertEquals?\b', re.I)

def git(*a, cwd):
    return subprocess.run(['git', *a], capture_output=True, text=True, cwd=cwd).stdout

def main(root):
    P = os.path.join(root, '.agent-pipeline')
    try: base = open(os.path.join(P, 'BASE')).read().strip() or 'main'
    except Exception: base = 'main'
    rng = f'{base}...HEAD'
    status = git('diff', '--name-status', rng, cwd=root)
    deleted = [l.split('\t', 1)[1] for l in status.splitlines() if l.startswith('D\t') and TEST_PATH.search(l.split('\t', 1)[1])]
    diff = git('diff', '-U0', rng, '--', '.', ':!.agent-pipeline', cwd=root)
    cur = None; per = {}
    for line in diff.splitlines():
        if line.startswith('+++ '):
            f = line[6:] if line.startswith('+++ b/') else None
            cur = f if f and TEST_PATH.search(f) else None
            continue
        if cur is None or line.startswith('---') or not line[:1] in '+-': continue
        d = per.setdefault(cur, {'cases_rm': 0, 'cases_add': 0, 'skip_add': [], 'assert_rm': 0, 'assert_add': 0})
        body = line[1:]
        if line[0] == '-':
            if CASE.search(body): d['cases_rm'] += 1
            if ASSERT.search(body): d['assert_rm'] += 1
        else:
            if CASE.search(body): d['cases_add'] += 1
            if ASSERT.search(body): d['assert_add'] += 1
            if SKIP.search(body): d['skip_add'].append(body.strip()[:120])
    flags = []
    for f in deleted: flags.append(f'- 刪除測試檔：`{f}`')
    for f, d in sorted(per.items()):
        if d['cases_rm'] > d['cases_add']: flags.append(f'- `{f}`：測試案例淨減 {d["cases_rm"] - d["cases_add"]}')
        if d['assert_rm'] > d['assert_add']: flags.append(f'- `{f}`：斷言淨減 {d["assert_rm"] - d["assert_add"]}')
        for s in d['skip_add']: flags.append(f'- `{f}`：新增 skip/xfail → `{s}`')
    added = sum(d['cases_add'] for d in per.values()); removed = sum(d['cases_rm'] for d in per.values())
    out = [f'# 測試稽核（{base}...HEAD，由 hook 產生）', '',
           f'測試檔變動：{len(per)} 個；案例 +{added} / −{removed}；刪除測試檔 {len(deleted)} 個', '']
    out += ['## ⚠️ 可能被移除或弱化', *flags] if flags else ['## 未發現測試被移除或弱化']
    out += ['', '_靜態比對 diff，可能誤報（例如重構搬移測試）。逐條確認。_', '']
    open(os.path.join(P, 'test-audit.md'), 'w', encoding='utf-8').write('\n'.join(out))

if __name__ == '__main__':
    try: main(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    except Exception: pass
