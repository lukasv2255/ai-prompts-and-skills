---
name: sync-pull
description: Stahne nejnovější verzi repozitare `ai-prompts-and-skills` a tim aktualizuje sdilene prompty a skilly v aktualnim prostredi. Pouzij kdyz uzivatel rika "sync pull", "synchronizuj prompty", "stahni skills", nebo chce aktualizovat globalni konfiguraci z Gitu.
---

# Sync Pull

Tento skill synchronizuje lokalni repozitar `ai-prompts-and-skills` z remote.

Pouzivej ho pro osobni operacni workflow, kdy je potreba dostat nejnovější sdilene
prompty, skilly a instrukce do aktualniho stroje bez ohledu na to, jestli bezi
na Macu nebo Windows.

## Cesta k repozitari

Repozitar se mezi stroji synchronizuje pres git (GitHub):

- macOS: `~/ai-prompts-and-skills`
- Windows: `C:/Users/tommy/Můj disk/AI-prompts-and-skills` (puvodni cesta na Google Disku, overit po odpojeni Drive)

Prakticky (Windows):

```bash
git -C "C:/Users/tommy/Můj disk/AI-prompts-and-skills" pull
```

Na jinem stroji pouzij cestu podle daneho OS vyse.

## Co udelat po pullu

- oznam, co se stahlo
- pripomen, ze zmeny je potreba propsat do `~/.claude/skills/` (na Windows jsou to reálné kopie, ne symlinky)

## Poznamky

- Je to osobni synchronizacni skill pro repozitar `ai-prompts-and-skills`, ne obecny git skill pro libovolny projekt.
- Pokud je worktree spinavy a `git pull` by kolidoval, nejdriv se zastav a rekni proc.

## Copy-paste: update instance z template (git)

Kdyz v klientske instanci plati konvence:

- `origin` = klientsky/instancni repo (tam pushujes)
- `template` = template upstream repo (odtud beres update)

pak update aktualni instance z template udelas takto:

```bash
git fetch template
git merge template/main
git push origin main
```
