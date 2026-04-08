---
name: sync-pull-mac
description: Stáhne nejnovější verzi globálního Claude nastavení z Gitu (AI Prompts and Skills repozitář) na Macu. Přes symlinky se automaticky aktualizuje ~/.claude/. Použij kdykoliv uživatel říká "sync pull mac", "synchronizuj na macu", nebo chce stáhnout prompty na Macu.
---

# Sync Pull (Mac)

> ⚠️ Před prvním použitím uprav cestu k repozitáři níže!

Cesta k repozitáři na tomto Macu: **`/Users/tommy/ai-prompts-and-skills`** *(uprav pokud je jiná)*

```bash
git -C "/Users/tommy/ai-prompts-and-skills" pull
```

Po dokončení oznam co bylo staženo. Změny se přes symlinky propíší do `~/.claude/`.
