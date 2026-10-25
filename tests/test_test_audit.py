#!/usr/bin/env python3
"""Run: python3 tests/test_test_audit.py — audit must flag deleted tests, removed cases, removed asserts, new skips."""
import os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__))
audit = os.path.join(here, '..', 'plugins', 'i-want-to-sleep', 'scripts', 'test_audit.py')
r = tempfile.mkdtemp(); g = lambda *a: subprocess.run(['git', *a], cwd=r, capture_output=True, check=True)
g('init', '-q', '-b', 'main'); g('config', 'user.email', 'a@b'); g('config', 'user.name', 't')
os.makedirs(f'{r}/tests'); os.makedirs(f'{r}/src')
open(f'{r}/tests/test_x.py', 'w').write("def test_a():\n    assert 1 == 1\n    assert 2 == 2\ndef test_b():\n    assert True\n")
open(f'{r}/tests/test_gone.py', 'w').write("def test_c():\n    assert 1\n")
open(f'{r}/src/a.py', 'w').write("x = 1\n")
g('add', '-A'); g('commit', '-qm', 'base'); g('checkout', '-qb', 'night-shift/x')
os.makedirs(f'{r}/.agent-pipeline'); open(f'{r}/.agent-pipeline/BASE', 'w').write('main')
open(f'{r}/tests/test_x.py', 'w').write('import pytest\n@pytest.mark.skip(reason="flaky")\ndef test_a():\n    assert 1 == 1\n')
g('rm', '-q', 'tests/test_gone.py'); g('commit', '-qam', 'night')
subprocess.run([sys.executable, audit, r], check=True)
out = open(f'{r}/.agent-pipeline/test-audit.md', encoding='utf-8').read()
checks = ['刪除測試檔：`tests/test_gone.py`', '測試案例淨減 1', '斷言淨減 2', '新增 skip/xfail']
bad = [c for c in checks if c not in out]
# clean case: only additions → no warnings
open(f'{r}/src/a.py', 'w').write("x = 2\n"); g('checkout', '-q', 'main'); g('checkout', '-qb', 'night-shift/clean')
open(f'{r}/tests/test_new.py', 'w').write("def test_n():\n    assert 1\n"); g('add', '-A'); g('commit', '-qm', 'add test')
subprocess.run([sys.executable, audit, r], check=True)
if '未發現測試被移除或弱化' not in open(f'{r}/.agent-pipeline/test-audit.md', encoding='utf-8').read(): bad.append('clean case')
for b in bad: print('FAIL', b)
print(f"{5-len(bad)}/5 passed"); sys.exit(1 if bad else 0)
