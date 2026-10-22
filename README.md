# i-want-to-sleep

[繁體中文](README.zh-TW.md)

Say **"I'm going to sleep"** in a Claude Code session and Claude takes over until morning:
opens a branch → finishes whatever the conversation left unfinished → keeps researching
competitors and best practices, picks the highest-value idea, implements and tests it,
commits, and moves on to the next one → leaves you a one-page report and a pushed branch
ready for a merge request.

## Install

### Ask your agent

Paste this into Claude Code:

> Install https://github.com/jaylooloomi/i-want-to-sleep

**If you are the AI agent reading this:** run these three commands in the shell, then
tell the user to read [Before each night](#before-each-night).

```bash
claude plugin marketplace add jaylooloomi/i-want-to-sleep
claude plugin install i-want-to-sleep@jaylooloomi
claude plugin list
```

### One-liner

```bash
curl -fsSL https://raw.githubusercontent.com/jaylooloomi/i-want-to-sleep/main/install.sh | bash
```

### Inside a Claude Code session

```
/plugin marketplace add jaylooloomi/i-want-to-sleep
/plugin install i-want-to-sleep@jaylooloomi
```

### Step by step (CLI)

```bash
# 1. Register this repo as a plugin marketplace
claude plugin marketplace add jaylooloomi/i-want-to-sleep

# 2. Install the plugin from it
claude plugin install i-want-to-sleep@jaylooloomi

# 3. Confirm
claude plugin list            # should show i-want-to-sleep@jaylooloomi  Status: enabled
claude plugin details i-want-to-sleep
```

### Try without installing

```bash
git clone https://github.com/jaylooloomi/i-want-to-sleep.git
claude plugin validate ./i-want-to-sleep                       # validates marketplace + plugin
claude --plugin-dir ./i-want-to-sleep/plugins/i-want-to-sleep
```

### Update / uninstall

```bash
claude plugin marketplace update jaylooloomi
claude plugin update i-want-to-sleep@jaylooloomi

claude plugin uninstall i-want-to-sleep@jaylooloomi
claude plugin marketplace remove jaylooloomi
```

Requires Claude Code v2.1.139 or later.

## Before each night

The plugin cannot set these for you. Do them once per machine (or per session where noted).

| Item | How | Why |
|---|---|---|
| Permissions | start with `claude --dangerously-skip-permissions` (or auto mode) | nobody is awake to approve tool calls |
| Stop-hook cap | `export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0` | Claude Code ends a turn after 8 consecutive stop-hook continuations by default; `0` removes the cap. The plugin has its own time and turn limits |
| Stop time / turn limit | `export NIGHT_SHIFT_STOP_AT=06:30` and `NIGHT_SHIFT_MAX_TURNS=120` (optional) | defaults are 06:30 local time / 120 turns |
| Push rights | the credential only needs to push to `night-shift/*`; protect `main` server-side | the hook only allows pushes to the night-shift branch; `main` protection is the server's job |
| Machine | keep it awake; on a subscription plan enable "continue when usage limit resets" | hitting the usage limit pauses the session |

## Use

In a Claude Code session that already has some work in progress:

```
/i-want-to-sleep:sleep
/i-want-to-sleep:sleep use the SQLite version as the baseline
/i-want-to-sleep:sleep wrap-up only
```

Or just say "I'm going to sleep" / "我要睡覺了".

## What happens overnight

| Step | What Claude does |
|---|---|
| 0 | Creates branch `night-shift/<date>`, sets the `.agent-pipeline/ACTIVE` flag |
| 1 | Reads the whole conversation and writes `scope.md`: original requirement, done, unfinished, rejected |
| 2 | Finishes every unfinished item, one commit each, with build + unit tests (3 retries, then `[WIP-FAILED]`) |
| 3 | Researches competitors / top open-source projects for ideas that serve the original requirement; records sources |
| 4 | Scores candidates `(Impact × Urgency) / (Effort × Blast)`; skips anything below 2 |
| 5 | Implements the winner with tests, one isolated commit per idea (`bonus-01`, `bonus-02`, …), then goes back to 4 |
| 6 | When time or turns run out: pushes the branch, writes `result.md`, posts a wrap-up report in the chat |

A **Stop hook** pushes Claude back to work every time it tries to stop while `ACTIVE` exists.
**PreToolUse hooks** block `git push` to anything but `night-shift/*`, `merge` / `rebase` /
`reset --hard` / `--force`, `rm -rf`, package installs, and edits to CI config, migrations,
settings files and dependency manifests. All hooks are inert when `ACTIVE` is absent, so
daytime sessions are unaffected.

## In the morning

1. Open the session: the last message is a wrap-up report (what was done, sources, test status, files changed, decisions needed).
2. The branch is already pushed: open a merge request and review the diff. Each bonus item is an independent commit — merge the good ones, `git revert` the rest.
3. Wrong direction? Give instructions in the same session.
4. Delete `.agent-pipeline/` after merging.

## Components

| File | Role |
|---|---|
| `plugins/i-want-to-sleep/skills/night-shift-job-generator/SKILL.md` | the procedure: scope → wrap-up → research → score → implement → report |
| `plugins/i-want-to-sleep/commands/sleep.md` | `/i-want-to-sleep:sleep` trigger |
| `plugins/i-want-to-sleep/hooks/hooks.json` + `scripts/night-shift-stop.sh` | Stop hook: keep working; request wrap-up at the time / turn limit |
| `plugins/i-want-to-sleep/scripts/guard-bash.sh`, `guard-write.sh` | PreToolUse guards |
| `.claude-plugin/marketplace.json` | makes this repo installable as a marketplace |
| `install.sh` | one-line installer |

## Limitations

- Claude Code only (CLI, desktop app, Remote Control). A claude.ai chat cannot run overnight.
- Guards are pattern-based blocklists and err on the side of not blocking normal commands; anything blocked is logged in `result.md`. Branch isolation plus a protected `main` is the real safety net.
- The 06:30 stop time uses the machine's local clock; check the time zone if Claude Code runs in a container.
- Not yet battle-tested. Watch the first few turns on the first night.

## License

MIT
