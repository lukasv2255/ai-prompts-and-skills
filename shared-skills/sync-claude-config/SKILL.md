---
name: sync-claude-config
description: Synchronizuje globální konfiguraci Clauda na GitHub. ~/.claude/CLAUDE.md a settings.json jsou symlinky do ~/ai-prompts-and-skills/claude/ — stačí git push/pull. Použij když uživatel napíše "sync push", "sync pull", "pushni claude config", "pullni config", nebo "synchronizuj nastavení".
---

# Sync Claude Config

`~/.claude/CLAUDE.md` a `~/.claude/settings.json` jsou symlinky přímo do `~/ai-prompts-and-skills/claude/`.
Žádné kopírování není potřeba — soubory jsou jedno a to samé.

## PUSH (uložit na GitHub)

```bash
cd ~/ai-prompts-and-skills
git add claude/CLAUDE.md claude/settings.json
git diff --cached --quiet && echo "Nic ke commitu." || (git commit -m "Sync Claude config" && git push && echo "Pushnuté.")
```

## PULL (stáhnout z GitHubu na tento počítač)

```bash
cd ~/ai-prompts-and-skills
git pull && echo "Aktualizováno."
```

## Postup

1. Zjisti z kontextu zda jde o push nebo pull
2. Spusť příslušný bash blok
3. Reportuj výsledek
