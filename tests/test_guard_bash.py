#!/usr/bin/env python3
"""Run: python3 tests/test_guard_bash.py  — exits non-zero on any mismatch."""
import json, os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__))
guard = os.path.join(here, '..', 'plugins', 'i-want-to-sleep', 'scripts', 'guard-bash.sh')
root = tempfile.mkdtemp(); os.makedirs(os.path.join(root, '.agent-pipeline')); open(os.path.join(root, '.agent-pipeline', 'ACTIVE'), 'w').close()
CASES = [
 (0,'git push -u origin night-shift/2026-10-23'), (0,'git push origin night-shift/2026-10-23'),
 (2,'git push origin main'), (2,'git push --force origin night-shift/x'), (2,'git push origin night-shift/x:main'),
 (2,'git push origin --delete night-shift/x'), (2,'git push'), (2,'cd repo && git push origin main'),
 (2,'git merge feature'), (2,'git reset --hard HEAD~1'), (2,'git checkout main'), (0,'git checkout -b night-shift/x'),
 (2,'rm -rf build'), (2,'rm -fr build'), (0,'rm -f foo.txt'),
 (2,'dotnet add package Polly'), (2,'npm install lodash'), (0,'npm install'), (2,'pip install requests'),
 (2,"sed -i 's/a/b/' appsettings.json"), (2,'echo x > .gitlab-ci.yml'), (0,'echo x > out.txt'),
 # former false positives (v0.5.0 blocked these)
 (0,'git commit -m "fix guard: git push x:y false positive"'),
 (0,"cat > .agent-pipeline/result.md <<'EOF'\n- guard blocked `git push origin a:b` in my notes\n- also mentions rm -rf and npm install lodash\nEOF"),
 (0,'echo "never git push to main" >> .agent-pipeline/result.md'),
 (0,'grep -n "git push" scripts/*.sh'), (0,'git log --oneline --grep "rm -rf"'),
 (0,"python3 -c \"print('git push origin main')\""), (0,'git commit -m "update appsettings.json docs"'),
]
env = dict(os.environ, CLAUDE_PROJECT_DIR=root); bad = 0
for exp, cmd in CASES:
    r = subprocess.run([guard], input=json.dumps({"tool_input": {"command": cmd}}), capture_output=True, text=True, env=env)
    if r.returncode != exp:
        bad += 1; print(f"FAIL expected {exp} got {r.returncode}: {cmd!r}")
print(f"{len(CASES)-bad}/{len(CASES)} passed"); sys.exit(1 if bad else 0)
