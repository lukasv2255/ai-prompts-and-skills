---
name: post-ig-pribeh
description: "Vygeneruje Instagram obsah pro PRIBEHOVE (historicke) posty AI-trener podle pipeline v src/promo/pribehy/: carousel (render_pribeh.py, 7 slidu, styl-plate misto avatara), reel (render_reel_kinetic.py -t archiv, tichy) a story (render_story_pribeh.py -> jedna title-card story.png primo v rootu postu). Postup: 01-myslenka -> 02-zneni podle pribeh-ramec.md -> dobova fotka jako predloha -> dry-run -> ukazka -> finalni post do 03-posts/NNN-slug."
---

# Post IG — pribehove (historicke) posty

Samostatna vetev pro **pribehova / historicka temata** (Kathrine Switzer, ctyrminutova
mile, historie pitneho rezimu). NENI to how-to obsah s brandovym avatarem — proto ma
vlastni pipeline, ne skill `post-ig`.

Assety jsou v `promo/pribehy/`, **skripty** v `src/promo/pribehy/`. Reel generator
je sdileny z `src/promo/pictures/render_reel_kinetic.py` (profil `archiv`).

Zdroj pravdy pro workflow:

- `promo/pribehy/00-nastaveni/pribeh-ramec.md` — dramaturgie, katalog motivu, fakta
- `promo/pribehy/00-nastaveni/styl-pribeh.md` — retro paleta, typografie, kompozice
- `src/promo/pribehy/render_pribeh.py`

Skill umi tri druhy vystupu do stejne post slozky `promo/pribehy/03-posts/NNN-<slug>/`:

- **carousel** — `render_pribeh.py` (7 slidu `1080x1350`, styl-plate + dobova fotka
  jako predloha, zadny avatar, zadne brandove razitko)
- **reel** — `render_reel_kinetic.py -t archiv` (`reel-kinetic-archiv.mp4` `1080x1920`,
  tichy, inkoustovy ramecek + rezavy progress bar, **bez rotace sablon** — pribehy
  jedou vzdy `archiv`)
- **story** — `render_story_pribeh.py` (jedna title-card `story.png` primo v rootu
  postu: clankovy titulek + poznamka "Cely pribeh ctete tady" + sipka; spodni tretina
  volna na rucni vlozeni odkazoveho stickeru v IG appce)

## Cim se lisi od `post-ig`

- **Zadny avatar, zadna rotace avatara** — identitu drzi retro paleta a dobova fotka.
- **Reel se nerotuje** — vzdy sablona `archiv` (historie se nelistuje prstem, ta se
  cte: bez swipu, silnejsi zrno, pomalejsi cteni). Zadny `reel-template.state.json`.
- **Story je jedna title-card**, ne 6 souboru. Zadny `gen_stories.py`, zadny
  `pick_scene.py`, zadny simple/codex render.
- **Paleta je vyhrazena** — retro (ink `#1a1512`, papir `#f2ebdd`, rezava `#e2703a`,
  mosaz `#c8a86b`). Sportovni paletu (navy/lime/electric) pribehy NESMI pouzit.

## Vstupy

- myslenka: `promo/pribehy/01-myslenka/<id>-<slug>.md`
- hotove zneni: `promo/pribehy/02-zneni/<id>-<slug>.md`
- volne historicke tema od uzivatele (vzdy se zdroji)

Kdyz uzivatel doda tema nebo myslenku, nejdriv vytvor / preprac
`promo/pribehy/02-zneni/<id>-<slug>.md`.

## Zneni

Zneni vzdy piš podle `promo/pribehy/00-nastaveni/pribeh-ramec.md`. Povinne casti:

- **H1 titulek** = pointa (odpovida slide 7, `Motiv: typo`).
- **`Story titulek: <clankovy titulek>`** hned pod H1 (samostatny radek). H1 sam o
  sobe rekne jen pointu, ne o CEM pribeh je — story-karta proto potrebuje clankovy
  titulek s tematem (napr. `Ctyrminutova mile: nerozhodl objem, rozhodla struktura`).
  Vzor: `<tema>: <pointa>`. Kdyz radek chybi, story spadne na H1.
- **`## Slib karuselu`** — co ctenar po precteni vi.
- **`## Karusel`** s pevnou dramaturgii **7 slidu**: hook -> kontext -> zvrat ->
  argument doby -> cena -> rozuzleni -> pointa/CTA. Kazdy screen `### Screen N`.
- U kazdeho screenu **`Motiv:`** z uzavreneho katalogu (skript neznamou hodnotu
  odmitne): `silueta`, `artefakt`, `osa`, `zakaz`, `krivka`, `typo`.
- **`Zvýraznit:`** — presna slova pro rezavy highlight.
- U silueta/foto screenu **`Předloha:`** (URL volne dobove fotky), **`Licence:`**,
  **`Výřez:`** a **`Scéna:`** — fotka slouzi jen jako layout reference, vystup je
  vzdy prekreslena ilustrace. Pouzivej jen prokazatelne volne snimky (Wikimedia
  Commons, `PD-anon-70-EU`, `CC0`). Pozor: `PD-US-no-notice` plati jen v USA, v EU
  ne.
- **`## Fakta`** — povinny blok (tvrzeni + zdroj). Vsechny letopocty a cisla z
  headlinu tady musi byt, jinak `render_pribeh.py` generovani odmitne.
- **`## Popisek`** + hashtagy.

## Render pipeline

Prikazy spoustej z korene projektu (`AI-trener`). Skripty pouzivaji `python3`.

### 1. Nacist kontext

- `promo/pribehy/00-nastaveni/pribeh-ramec.md`
- `promo/pribehy/00-nastaveni/styl-pribeh.md`
- vstupni `01-myslenka` / `02-zneni`
- pri renderu i `src/promo/pribehy/render_pribeh.py`, kdyz si nejsi jisty argumenty

### 2. Pripravit zneni

Vytvor / uprav `02-zneni/<id>-<slug>.md` podle ramce. Dohledej dobove fotky
(volna licence) a zapiš je do `Předloha:`. Nezapomen na `Story titulek:` a `## Fakta`.

### 3. Dry-run

```bash
python3 src/promo/pribehy/render_pribeh.py --zneni <id>-<slug> --dry-run
```

Over, ze parser nasel 7 screenu, spravne motivy, highlighty a ze letopocty z
headlinu jsou pokryte v `## Fakta`.

### 4. Ukazkovy slide

```bash
python3 src/promo/pribehy/render_pribeh.py --zneni <id>-<slug> --only 1
```

### 5. Dogenerovat carousel

```bash
python3 src/promo/pribehy/render_pribeh.py --zneni <id>-<slug>
```

Jen prerezat hotove raw (bez nove generace): `--recrop`. Vystup: `01-*.png` az
`07-*.png` v rootu post slozky, originaly v `raw/`, stazene predlohy v `predlohy/`.

### 6. Reel (sablona archiv, tichy)

Reel skladej ze slidu hotoveho carouselu sdilenym generatorem. Pribehy jedou
**vzdy** profil `archiv` — nerotuj sablony. Protoze `render_reel_kinetic.py`
resolvuje `--post` proti `promo/pictures/`, pro pribehy predej **`--slides-dir`**
(plna cesta k post slozce) a **`--zneni`** (plna cesta ke zneni pribehu):

```bash
python3 src/promo/pictures/render_reel_kinetic.py \
  --slides-dir "promo/pribehy/03-posts/NNN-<slug>" \
  --template archiv \
  --zneni "promo/pribehy/02-zneni/NNN-<slug>.md"
```

Vystup `reel-kinetic-archiv.mp4` (`1080x1920`, ~24 s, tichy — trending audio se
pridava az v IG appce). Bez `--bpm` casuje skript delku kazdeho slidu podle **poctu
znaku** cteneho textu ve zneni (v cestine lepsi proxy cteni nez pocet slov). `--bpm`
nezadavej — pribehove reely nesnapujeme na beat.

### 7. Story (jedna title-card)

```bash
python3 src/promo/pribehy/render_story_pribeh.py --post NNN-<slug>
```

Vygeneruje jednu `story.png` (`1080x1920`) **primo v rootu postu**. Titulek bere
z radku `Story titulek:` ve zneni (fallback H1). Prepis lze pres `--title "..."`,
poznamku nad odkaz pres `--note "..."` (vychozi "Celý příběh čtěte tady").
Spodni tretina zustava volna — odkazovy sticker vklada uzivatel rucne v IG appce.

## Kontrola

- **carousel:** 7 finalnich PNG v rootu post slozky, rozmer `1080x1350`, odpovidajici
  originaly v `raw/`, retro paleta (ne sportovni), zadny avatar ani logo,
- **reel:** existuje `reel-kinetic-archiv.mp4`, format `1080x1920`, tichy,
- **story:** jedna `story.png` v rootu postu, rozmer `1080x1920`, titulek rekne o CEM
  pribeh je (tema + pointa), spodni tretina volna na sticker,
- letopocty/cisla z headlinu jsou v `## Fakta`,
- ceska diakritika v obrazku neni rozbita (over vizualne otevrenim PNG),
- predlohy pouzivaji jen prokazatelne volne licence.

## Report

Na konci rekni:

- ktery `02-zneni` byl vytvoren / upraven (a jestli doplnen `Story titulek:`),
- jake soubory vznikly (carousel `01-07`, `reel-kinetic-archiv.mp4`, `story.png`)
  a kam,
- jaky titulek story dostala,
- jestli prosla kontrola rozmeru, palety a diakritiky,
- pokud neco neproslo, navrhni jednu cilenou dalsi iteraci.
