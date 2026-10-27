# Pravidla stábní kultury složek

Platí pro každý **projekt** (složka aktuálního VS Code workspace), každou jeho právní
**agendu** (`agendy` v `projekty.json`) a každý **prvek** (`prvky`: prvky Evolia jako `evolio/sablony`,
`evolio/emachine`… — seznam smí obsahovat vnořené cesty). Projekt, agenda i prvek jsou „jednotka“;
kostra D8 platí jen pro agendy.

| ID | Pravidlo | Kontrola |
|---|---|---|
| D1 | `docs/` obsahuje jen statické soubory: žádné skripty, logy, databáze; nic do něj nezapisuje automatizace (launchd, cron) | script |
| D2 | Každá jednotka má `docs/` a v něm `projekt-<jméno>.md`, `roadmap.md`, `todo.md`. Nikde jinde tyto soubory nejsou | script |
| D3 | Každá jednotka má `backup/` — jen na zálohy před velkou změnou, **ne na archiv** | script |
| D4 | Co nejvíc statických souborů žije v `docs/` | script najde kandidáty, rozhoduje úsudek |
| D5 | `docs/` je členěné do podadresářů (klidně s jedním souborem); v kořeni `docs/` jsou jen tři soubory z D2 | script |
| D6 | Kód (`.py`, `.sh`) je jen v `src/` jednotky — žádné `tools/` ani `scripts/`; vyřazené skripty v `src/archiv/<téma>/`. `src/` je povinné jen tam, kde je kód | script |
| D7 | `<agenda>/sablony-evolio/` (vzory do Evolia pro jednu agendu) má pevnou strukturu: v kořeni jen `workflow.md` a `pravidla-agendy.md`, pak složka `NN-nazev/` pro každý vzor. Ve vzoru `zdroj.md` a `mapovani-parametru.md` (povinné), další `.md` a `.docx` (`zaklad.docx`, `<vzor>.docx`, pracovní poznámky) a jen podsložky `predloha/`, `hotove/`, `hotove-stare/`, `revize/` | script |
| D8 | **Kostra právní agendy** (`agendy` v `projekty.json`): `backup/`, `docs/`, `automatizace/`, `sablony-evolio/`, `prompty/` — v `prompty/` jen podadresáře pojmenované podle promptu. Nic jiného v kořeni agendy (volitelně `src/` kvůli D6, `README.md`/`CLAUDE.md`) | script |
| D9 | **Každá automatizace** (podsložka `automatizace/`, v agendě i v `evolio/emachine/automatizace/`) má v kořeni `README.md` (podrobnosti, měření, testy), `roadmap.md` (verze a další kroky), `todo.md` a `workflow.md` (cílový postup) | script |
| D10 | **Repo s nesouvisejícími projekty** (`kod` / `staticke` v `projekty.json`): mimo podprojekty jsou jen jejich nadřazené složky, meta soubory repa (`README.md`, `CLAUDE.md`, `Dockerfile`…) a výjimky z `vyjimky_koren` | script |

## Upřesnění

- **Podprojekty:** repo s víc nesouvisejícími projekty (AI-brand-me) se v `projekty.json`
  rozdělí na `kod` a `staticke`. Podprojekt s kódem je jednotka s plnými pravidly D1–D9
  (vlastní `docs/`, `src/`, `backup/`, `projekt-<jméno>.md`). Statický podprojekt drží
  jen dokumenty kdekoli ve své struktuře; hlásí se v něm jen kód (D6) a logy či databáze
  (D1). Vnořený podprojekt (`job-rohlik/portal/bot` v `job-rohlik`) se kontroluje jen sám
  za sebe. Cesty v nálezech jsou relativně ke kořeni repa.

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
  kde soubory žijí z podstaty jinde: kód a šablony (`web`, `src`, `sablony`, `sablony-evolio` — pravidlo D7, `automatizace` — kostra D8, `prompty`,
  `skills`, `styles`…), výstupy automatizací (`reports`, `digests`, `prilohy`, `logs`,
  `data`… — v `docs/` by porušily D1) a `tasks/` (globální konvence `tasks/lessons.md`).
  Extra výjimky pro projekt: klíč `"vyjimky"` v `projekty.json`.
- **D6 nehlásí:** skripty skillů (`skills/`), testy (`tests/`) a vstupní bod vedle
  vlastního `src/` (`main.py` + `src/`).
- **D2 nehlásí:** `roadmap.md` / `todo.md` v kořeni automatizace (D9) a `roadmap.md` / `todo.md` / `projekt-*.md` v `src/<podprojekt>/docs/` — podadresář
  `src/` smí být malý projekt sám o sobě (vlastní výstup, dashboard) s vlastním plánem.
- **`backup/`** se při kontrole neprochází — zálohy smí obsahovat kopie čehokoli.
  Skill do `backup/` nikdy nic nenavrhuje přesunout; archiv patří do `src/archiv/` (kód)
  nebo `docs/archiv/` (dokumenty).

## Přidání pravidla

Strojově ověřitelné → nová kontrola ve `zkontroluj()` v `check.py` + řádek sem.
Jen úsudkové → řádek sem s kontrolou „úsudek“; skill ho projde při čtení.
