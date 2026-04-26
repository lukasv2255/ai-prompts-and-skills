---
name: sync-push
description: Nahraje aktualni stav repozitare `ai-prompts-and-skills` na GitHub a tim zverejni nove sdilene prompty a skilly pro ostatni stroje. Pouzij kdyz uzivatel rika "sync push", "pushni prompty", "uloz skills na git", nebo chce publikovat zmeny globalni konfigurace.
---

# Sync Push

Tento skill pushuje zmeny v repozitari `ai-prompts-and-skills` na remote.

Pouzivej ho po upravach sdilenych promptu, skillu nebo globalnich instrukci, kdy
je potreba dostat zmeny z aktualniho stroje na GitHub a nasledne i na ostatni
zarizeni.

## Cesta k repozitari

Nehardcoduj jmeno uzivatele. Preferuj home directory:

- macOS / Linux: `~/ai-prompts-and-skills`
- Windows: `~/ai-prompts-and-skills` nebo odpovidajici cesta z home directory

Prakticky:

```bash
git -C "$HOME/ai-prompts-and-skills" add -A
git -C "$HOME/ai-prompts-and-skills" commit -m "sync: update prompts and skills"
git -C "$HOME/ai-prompts-and-skills" push
```

Kdyz neni co commitovat, jen to oznam.

## Pravidla

- Pred commitem zkontroluj `git status`, at je jasne, co se pushuje.
- Je to osobni synchronizacni skill pro `ai-prompts-and-skills`, ne obecny release workflow.
- Pokud uzivatel chce jinou commit message, nech ji upravit.
