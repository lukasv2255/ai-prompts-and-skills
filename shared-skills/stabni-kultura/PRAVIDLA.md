# Pravidla stábní kultury složek

Platí pro každý **projekt** (složka aktuálního VS Code workspace) a každou jeho
**agendu** (výslovný seznam v `projekty.json`). Agenda je i prvek Evolia (`evolio/sablony`,
`evolio/emachine`…) — seznam smí obsahovat vnořené cesty. Projekt i agenda jsou „jednotka“.

| ID | Pravidlo | Kontrola |
|---|---|---|
| D1 | `docs/` obsahuje jen statické soubory: žádné skripty, logy, databáze; nic do něj nezapisuje automatizace (launchd, cron) | script |
| D2 | Každá jednotka má `docs/` a v něm `projekt-<jméno>.md`, `roadmap.md`, `todo.md`. Nikde jinde tyto soubory nejsou | script |
| D3 | Každá jednotka má `backup/` — jen na zálohy před velkou změnou, **ne na archiv** | script |
| D4 | Co nejvíc statických souborů žije v `docs/` | script najde kandidáty, rozhoduje úsudek |
| D5 | `docs/` je členěné do podadresářů (klidně s jedním souborem); v kořeni `docs/` jsou jen tři soubory z D2 | script |
| D6 | Kód (`.py`, `.sh`) je jen v `src/` jednotky — žádné `tools/` ani `scripts/`; vyřazené skripty v `src/archiv/<téma>/`. `src/` je povinné jen tam, kde je kód | script |

## Upřesnění

- **Jméno jednotky** v `projekt-<jméno>.md` = název složky malými písmeny
  (`projekt-springwalk.md`, `projekt-ulov-domov.md`).
- **D1 zakázané přípony:** `.py .sh .js .ts .log .db .sqlite .plist` a podobné (seznam
  `ZAKAZANE_PRIPONY` v `check.py`).
- **D1 zápis automatizací:** podle přípony se nepozná, že do statického souboru někdo
  průběžně zapisuje. Proto `check.py` hlásí navíc (a) datové soubory v `docs/` se jménem
  stavu (`progress`, `state`, `cache`, `seen`, `fronta`…), (b) řádky v kódu launchd/cron
  agentů, které obsahují cestu do `docs/`. Obojí je kandidát — jestli jde o čtení, nebo
  zápis, rozhoduje skill přečtením kódu.
- **D4 nehlásí:** `README.md`, `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, a obsah složek,
  kde soubory žijí z podstaty jinde: kód a šablony (`web`, `src`, `sablony`, `prompty`,
  `skills`, `styles`…), výstupy automatizací (`reports`, `digests`, `prilohy`, `logs`,
  `data`… — v `docs/` by porušily D1) a `tasks/` (globální konvence `tasks/lessons.md`).
  Extra výjimky pro projekt: klíč `"vyjimky"` v `projekty.json`.
- **D6 nehlásí:** skripty skillů (`skills/`), testy (`tests/`) a vstupní bod vedle
  vlastního `src/` (`main.py` + `src/`).
- **`backup/`** se při kontrole neprochází — zálohy smí obsahovat kopie čehokoli.
  Skill do `backup/` nikdy nic nenavrhuje přesunout; archiv patří do `src/archiv/` (kód)
  nebo `docs/archiv/` (dokumenty).

## Přidání pravidla

Strojově ověřitelné → nová kontrola ve `zkontroluj()` v `check.py` + řádek sem.
Jen úsudkové → řádek sem s kontrolou „úsudek“; skill ho projde při čtení.
