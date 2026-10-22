<h1 align="center">i-want-to-sleep</h1>

<p align="center">
  <b>Say "I'm going to sleep". Wake up to finished work, a tested branch, and a report.</b><br>
  A Claude Code plugin that takes over your session for N hours.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <img src="https://img.shields.io/badge/version-0.3.0-informational" alt="version">
  <img src="https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.139-orange" alt="Claude Code ≥ 2.1.139">
  <img src="https://img.shields.io/badge/harness-Claude%20Code%20only-lightgrey" alt="Claude Code only">
  <a href="README.zh-TW.md"><img src="https://img.shields.io/badge/lang-繁體中文-green" alt="繁體中文"></a>
</p>

<p align="center"><img src="docs/hero-en-v2.png" alt="Before: a sleepy octopus at a laptop. /sleep 8. After: the same octopus in a hard hat, eight tentacles holding a wrench, keyboard, coffee, a green tests-passed badge, a git branch, a magnifier, a notebook, and typing — the terminal reads tests passed." width="900"></p>

## Quick start

```bash
claude plugin marketplace add jaylooloomi/i-want-to-sleep
claude plugin install i-want-to-sleep@jaylooloomi
export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0
claude --dangerously-skip-permissions
```

Then, in a session that already has work in progress:

```
/i-want-to-sleep:sleep 8
```

Come back in 8 hours. The last message in the session is a wrap-up report; the branch `night-shift/<date>` is pushed and ready for a merge request.

## Why

You stop working at midnight with a half-finished feature. The model could keep going — it has the context, it can run the tests — but every turn ends with "anything else?" and nobody is there to say yes.

This plugin removes that stop. It turns the open session into a bounded, guarded autonomous run:

| Without | With |
|---|---|
| Work stops when you do | Work continues for the hours you specify |
| Context is lost overnight | The conversation is compressed into `scope.md` and used as the contract |
| "Autonomous" agents wander off-scope | Bonus work must trace back to your original requirement, scored, with a minimum bar |
| Agents push to main / install deps / touch CI | Hard-blocked by PreToolUse hooks, not by prompt text |
| You review a 2,000-line diff | One commit per item; merge the good ones, `git revert` the rest |

## How it works

```
/sleep 8
   │
   ▼
Step 0  branch night-shift/<date>, ACTIVE flag, DEADLINE = now + 8h
Step 1  read the whole conversation → scope.md (requirement / done / unfinished / rejected)
Step 2  finish every unfinished item — one commit each, build + unit tests, 3 retries
Step 3  research competitors & top projects for ideas that serve the original requirement
Step 4  score (Impact × Urgency) / (Effort × Blast); skip anything < 2
Step 5  implement the winner with tests — one isolated commit (bonus-01, bonus-02, …)
   ▲                         │
   └── back to Step 4 ◄──────┘   until the deadline
Step 6  push branch, write result.md, post the wrap-up report in chat
```

Two mechanisms make this run unattended:

- **Stop hook** — every time Claude tries to end its turn while `.agent-pipeline/ACTIVE` exists, the hook sends it back with the next instruction. At the deadline it asks for wrap-up once, then lets go.
- **PreToolUse hooks** — deterministic shell scripts (no model involved) that block `git push` to anything but `night-shift/*`, `merge` / `rebase` / `reset --hard` / `--force`, `rm -rf`, package installs, and edits to CI config, migrations, settings files and dependency manifests.

All hooks are inert when `ACTIVE` is absent. Daytime sessions are unaffected.

## Usage

```
/i-want-to-sleep:sleep               # 8 hours (default)
/i-want-to-sleep:sleep 2             # 2 hours — works in the daytime too
/i-want-to-sleep:sleep 8 use the SQLite version as the baseline
/i-want-to-sleep:sleep 1 wrap-up only
```

The first number is the duration in hours. Anything after it is passed to the skill as instructions. Saying "I'm going to sleep" or "take over for 3 hours" in plain language also triggers it.

### In the morning

1. Read the wrap-up report in the session (what was done, sources, test status, files, decisions needed). Details in `.agent-pipeline/result.md`.
2. Open a merge request from `night-shift/<date>`. Each bonus item is an independent commit.
3. Wrong direction? Say so in the same session.
4. Delete `.agent-pipeline/` after merging.

## Install

<details>
<summary><b>Ask your agent</b></summary>

Paste into Claude Code:

> Install https://github.com/jaylooloomi/i-want-to-sleep

**If you are the AI agent reading this**, run:

```bash
claude plugin marketplace add jaylooloomi/i-want-to-sleep
claude plugin install i-want-to-sleep@jaylooloomi
claude plugin list
```

Then tell the user to read [Configuration](#configuration).
</details>

<details>
<summary><b>One-liner</b></summary>

```bash
curl -fsSL https://raw.githubusercontent.com/jaylooloomi/i-want-to-sleep/main/install.sh | bash
```
</details>

<details>
<summary><b>Inside a Claude Code session</b></summary>

```
/plugin marketplace add jaylooloomi/i-want-to-sleep
/plugin install i-want-to-sleep@jaylooloomi
```
</details>

<details>
<summary><b>Try without installing</b></summary>

```bash
git clone https://github.com/jaylooloomi/i-want-to-sleep.git
claude plugin validate ./i-want-to-sleep
claude --plugin-dir ./i-want-to-sleep/plugins/i-want-to-sleep
```
</details>

<details>
<summary><b>Update / uninstall</b></summary>

```bash
claude plugin marketplace update jaylooloomi
claude plugin update i-want-to-sleep@jaylooloomi

claude plugin uninstall i-want-to-sleep@jaylooloomi
claude plugin marketplace remove jaylooloomi
```
</details>

## Configuration

The plugin cannot set these for you.

| Setting | Value | Required | Why |
|---|---|---|---|
| Permission mode | `claude --dangerously-skip-permissions` (or auto mode) | **yes** | nobody is awake to approve tool calls |
| `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` | `0` | **yes** | Claude Code ends a turn after 8 consecutive stop-hook continuations by default; `0` removes the cap. The plugin enforces its own deadline and turn limit |
| `NIGHT_SHIFT_HOURS` | hours, default `8` | no | used only when `/sleep` gets no number |
| `NIGHT_SHIFT_MAX_TURNS` | integer, default `120` | no | turn-count safety net |
| Git credentials | push access to `night-shift/*`; protect `main` server-side | — | the hook only allows pushes to the night-shift branch; `main` protection is the server's job |
| Machine | keep awake; on a subscription plan, enable "continue when usage limit resets" | — | hitting the usage limit pauses the session |

Put the two exports in `~/.zshrc` / `~/.bashrc`. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0` is safe globally: this plugin's Stop hook only blocks while `ACTIVE` exists.

## Compatibility

| Harness | Status |
|---|---|
| Claude Code (CLI, desktop app, Remote Control) ≥ 2.1.139 | ✅ supported |
| claude.ai web / mobile chat | ❌ cannot run a session unattended |
| OpenAI Codex CLI, Cursor, Gemini CLI, Copilot CLI, … | ❌ not yet — the skill, the `/sleep` command and both hooks are packaged as a Claude Code plugin |

This plugin does not use `/goal`; it is built on Claude Code's Stop and PreToolUse hooks. Codex, Cursor, Gemini CLI and Copilot CLI all have stop-hook equivalents (see [goal-loop](https://github.com/bodecloud/goal-loop) for a cross-harness example), so a port is feasible: the procedure (`SKILL.md`) moves as-is, the two shell guards need each harness's hook format. PRs welcome.

## What's in the box

| Path | Role |
|---|---|
| `plugins/i-want-to-sleep/skills/night-shift-job-generator/SKILL.md` | the procedure: scope → wrap-up → research → score → implement → report |
| `plugins/i-want-to-sleep/commands/sleep.md` | `/i-want-to-sleep:sleep [hours] [instructions]` |
| `plugins/i-want-to-sleep/hooks/hooks.json` | registers the three hooks |
| `plugins/i-want-to-sleep/scripts/night-shift-stop.sh` | Stop hook: keep working; request wrap-up at the deadline |
| `plugins/i-want-to-sleep/scripts/guard-bash.sh` | PreToolUse guard for shell commands |
| `plugins/i-want-to-sleep/scripts/guard-write.sh` | PreToolUse guard for file writes |
| `.claude-plugin/marketplace.json` | makes this repo installable as a marketplace |
| `install.sh` | one-line installer |

## FAQ

**Will it push to `main`?**
No. The Bash guard allows `git push` only to `night-shift/*`, never with `--force` or `--delete`. Protect `main` on the server anyway — the guard is a blocklist and blocklists can be circumvented.

**Will it install dependencies?**
No. `dotnet add package`, `npm install <pkg>`, `pip install` and similar are blocked. Ideas that need a new dependency go to `result.md` under "decisions needed".

**What stops it from drifting off-topic?**
Every bonus candidate must be written as "because the requirement is X, top implementations also do Y" and must cite a source. Anything that cannot be phrased that way is dropped. Candidates scoring below 2 are skipped.

**What if the build is broken at the deadline?**
It commits the state as `[WIP-FAILED]`, explains the blocker in `result.md`, and still writes the report. Nothing is force-pushed or reverted.

**Does it remember previous nights?**
No, by design. Each run reads only the current conversation and the current repo. `.agent-pipeline/` is wiped at Step 0.

**Does it work in the daytime?**
Yes. `/sleep 2` is a two-hour handover. The name is a joke; the deadline is not.

## Limitations

- Guards are pattern-based blocklists tuned to avoid blocking normal commands; a determined model can find a way around them. Branch isolation plus a protected `main` is the real safety net.
- The wrap-up report format is a skill instruction; if the context is compacted mid-run, the report may deviate. `result.md` is the source of truth.
- Not yet battle-tested at scale. Watch the first few turns of your first run.

## Contributing

Issues and PRs welcome. Run `claude plugin validate .` before opening a PR. If you port the procedure to another harness, open an issue — a link from Compatibility is yours.

## License

[MIT](LICENSE)
