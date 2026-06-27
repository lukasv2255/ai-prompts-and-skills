# AI Prompts and Skills

Shared setup for Claude and Codex across multiple computers.

## What Is In This Repo

- `shared-skills/` is the single source of truth for reusable skills.
- `claude/` contains Claude-specific global files.
- `codex/` contains Codex global instructions and template config.
- `scripts/` contains Windows setup scripts for linking local folders to this repo.

## What To Sync

- Shared skills for both tools
- Claude global prompt in `claude/CLAUDE.md`
- Claude custom agents in `claude/agents/`
- Claude starter hooks in `claude/hooks/` (wired up by `claude/settings.template.json`)
- Optional template settings in `claude/settings.template.json`
- Codex global instructions in `codex/AGENTS.md`
- Optional Codex template config in `codex/config.template.toml`

## Hooks and settings — two layers

There are two separate hook setups, do not confuse them:

1. **Version-controlled starter (in this repo).** `claude/settings.template.json`
   wires up the scripts in `claude/hooks/` (e.g. `check-project-structure.sh`).
   Use this as the clean starting point on a fresh machine. Paths use
   `<username>` placeholders — replace them for the local OS/user.

2. **Live machine config (`claude/settings.json`).** The actual day-to-day setup
   points its hooks at an external install, **`claude-leverage`**, under
   `~/.local/share/claude-leverage/scripts/hooks/` (stack-freshness,
   block-secrets-precommit, context-surface, …). **These scripts are NOT in this
   repo** — `claude-leverage` is a separate, machine-local tool. The absolute
   `/Users/lukas/...` path is intentional (Mac is the primary machine).

   To reproduce the live setup on another machine you must install
   `claude-leverage` there separately; pulling this repo alone is not enough.
   If you ever want these hooks version-controlled here, copy the scripts into
   `claude/hooks/` on the Mac and repoint `settings.json` at them.

## What Not To Sync

- Auth files
- Session history
- Cache, logs, sqlite/state files
- Per-machine local runtime data

For Codex this means especially:

- do not sync `~/.codex/auth.json`
- do not sync sqlite, logs, cache or sessions from `~/.codex/`
- do sync `~/.codex/AGENTS.md` and the template source in `codex/`
- do link shared skills into `~/.agents/skills/`

## Windows Setup

Clone this repo somewhere stable, for example:

```powershell
git clone https://github.com/lukasv2255/ai-prompts-and-skills.git C:\Users\<username>\ai-prompts-and-skills
```

Then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-claude.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\install-codex.ps1
```

`install-codex.ps1` does this:

- copies `codex/AGENTS.md` to `~/.codex/AGENTS.md`
- copies `codex/config.template.toml` to `~/.codex/config.toml` if it does not exist yet
- links every folder from `shared-skills/` into `~/.agents/skills/`

## Daily Workflow

On computer A:

```powershell
git add .
git commit -m "Update skills"
git push origin master
```

On computer B:

```powershell
git pull origin master
```

After pull, Claude and Codex use the updated files through local junctions.
