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

Nehardcoduj jmeno uzivatele. Preferuj home directory:

- macOS / Linux: `~/ai-prompts-and-skills`
- Windows: `~/ai-prompts-and-skills` nebo odpovidajici cesta z home directory

Prakticky:

```bash
git -C "$HOME/ai-prompts-and-skills" pull
```

Kdyz shell nebo prostredi nepouziva `$HOME`, odvod cestu z domovske slozky daneho
uzivatele misto natvrdo zapsaneho `lukas` nebo `tommy`.

## Co udelat po pullu

- oznam, co se stahlo
- pripomen, ze symlinky propisuji zmeny do `~/.claude/`, `~/.agents/skills/` nebo dalsich napojenych mist

## Poznamky

- Je to osobni synchronizacni skill pro repozitar `ai-prompts-and-skills`, ne obecny git skill pro libovolny projekt.
- Pokud je worktree spinavy a `git pull` by kolidoval, nejdriv se zastav a rekni proc.
