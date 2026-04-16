---
name: sync-pull-pc
description: Stáhne nejnovější verzi globálního Claude nastavení z Gitu na Windows PC (AI Prompts and Skills repozitář). Přes symlinky se automaticky aktualizuje ~/.claude/. Použij kdykoliv uživatel říká "sync pull", "sync pull pc", "synchronizuj", "stáhni prompty", nebo chce stáhnout globální Claude nastavení z GitHubu na PC.
---

# Sync Pull (PC)

Repozitář na tomto počítači: `C:/Users/tommy/ai-prompts-and-skills`

```bash
git -C "C:/Users/tommy/ai-prompts-and-skills" pull
```

Po dokončení oznam co bylo staženo. Změny se přes symlinky propíší do `~/.claude/`.
