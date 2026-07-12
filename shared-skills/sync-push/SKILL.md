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

Repozitar je na Google Disku (synchronizuje se mezi stroji):

- Windows: `C:/Users/tommy/Můj disk/AI-prompts-and-skills`
- macOS: odpovidajici cesta ke Google Disku; jmeno slozky `AI-prompts-and-skills` zustava stejne

Prakticky (Windows):

```bash
git -C "C:/Users/tommy/Můj disk/AI-prompts-and-skills" add -A
git -C "C:/Users/tommy/Můj disk/AI-prompts-and-skills" commit -m "sync: update prompts and skills"
git -C "C:/Users/tommy/Můj disk/AI-prompts-and-skills" push
```

Kdyz neni co commitovat, jen to oznam.

## Pravidla

- Pred commitem zkontroluj `git status`, at je jasne, co se pushuje.
- Je to osobni synchronizacni skill pro `ai-prompts-and-skills`, ne obecny release workflow.
- Pokud uzivatel chce jinou commit message, nech ji upravit.

## Copy-paste: push instance po merge z template

Po `git merge template/main` v klientske instanci typicky jen:

```bash
git push origin main
```
