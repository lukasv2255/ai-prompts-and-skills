---
name: sync-push-pc
description: Nahraje aktuální stav AI Prompts and Skills repozitáře na GitHub (git add, commit, push) na Windows PC. Použij kdykoliv uživatel říká "sync push", "sync push pc", "pushni prompty", "ulož skills na git", nebo chce nahrát globální Claude nastavení na GitHub z PC.
---

# Sync Push (PC)

Repozitář na tomto počítači: `C:/Users/tommy/ai-prompts-and-skills`

```bash
git -C "C:/Users/tommy/ai-prompts-and-skills" add -A
git -C "C:/Users/tommy/ai-prompts-and-skills" commit -m "sync: update prompts and skills"
git -C "C:/Users/tommy/ai-prompts-and-skills" push
```

Pokud není co commitovat, jen to oznam. Po dokončení oznam co bylo pushnuté.
