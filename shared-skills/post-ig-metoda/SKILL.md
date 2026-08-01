---
name: post-ig-metoda
description: "Vygeneruje Instagram obsah pro METODICKE (klinicke, datove) posty AI-trener podle pipeline v src/promo/metody/: carousel (render_metoda.py, 7 slidu, deterministicky PIL bez AI modelu, svetla klinicka paleta), reel (render_reel_kinetic.py -t metoda, tichy) a story (render_story_metoda.py -> jedna title-card story.png v rootu postu). Zneni NEPISE clovek rucne — vyrobi ho content-engine prikaz `karusel` z tematu KB (topic -> LLM -> 02-zneni). Postup: promo/content-engine `karusel --topic-id/--sport` -> 02-zneni/NNN-slug.md -> dry-run -> ukazka -> finalni post do 03-posts/NNN-slug."
---

# Post IG — metodicke (klinicke, datove) posty

Treti samostatna vetev vedle `post-ig` (brandovy avatar) a `post-ig-pribeh` (historie).
Obsah je **metodicky how-to podlozeny daty z knihovny metod** (VO2 max, laktatovy prah,
polarizovany trenink). Nekresli se AI obrazkovym modelem — sazi se **typograficky v PIL**,
takze diakritika se nemuze rozbit, render je zdarma a deterministicky.

Klicovy rozdil oproti obema ostatnim vetvim: **zneni se negeneruje rucne.** Vyrobi ho
content-engine z tematu znalostni baze — tema (shluk tvrzeni se zdroji) projde levnym LLM
a vypadne markdown zneni ve tvaru, ktery umi `render_metoda.py`. Zdroje (`## Fakta`) se
sestavi deterministicky z odkazu tvrzeni, model si je nevymysli.

Assety jsou v `promo/metody/`, **skripty** v `src/promo/metody/`. Reel generator je
sdileny z `src/promo/pictures/render_reel_kinetic.py` (profil `metoda`). Bridge KB->zneni
je v `promo/content-engine/` (prikaz `karusel`).

Zdroj pravdy pro workflow:

- `promo/metody/00-nastaveni/metoda-ramec.md` — dramaturgie 7 slidu, katalog typu, fakta
- `promo/metody/00-nastaveni/styl-metoda.md` — svetla klinicka paleta, typografie, rozmery
- `promo/content-engine/prompts/karusel.md` — system prompt pro tema -> zneni
- `src/promo/metody/render_metoda.py`

Skill umi tri druhy vystupu do stejne post slozky `promo/metody/03-posts/NNN-<slug>/`:

- **carousel** — `render_metoda.py` (7 slidu `1080x1350`, klinicka data-karta, evidence
  odznak s barevnou teckou podle sily dukazu, tlumeny wordmark `trenzo.cz` vpravo dole)
- **reel** — `render_reel_kinetic.py -t metoda` (`reel-kinetic-metoda.mp4` `1080x1920`,
  tichy, svetly papirovy ramecek + evidence-teal progress bar, velmi slabe zrno,
  **bez rotace sablon** — metody jedou vzdy `metoda`, data se ctou, ne listuji)
- **story** — `render_story_metoda.py` (jedna title-card `story.png` primo v rootu postu:
  titulek metody + poznamka "Celá metoda v karuselu" + sipka; spodni tretina volna na
  rucni vlozeni odkazoveho stickeru v IG appce)

## Cim se lisi od `post-ig` a `post-ig-pribeh`

- **Zadny AI obrazkovy model** — carousel i story se sazi v PIL. Zadny avatar, zadna
  dobova fotka, zadne predlohy. Obsah je typografie + cisla + evidence odznak.
- **Zneni pise stroj, ne clovek** — vstup je tema z KB, ne rucne psana myslenka. Ty jen
  vybirous tema (nebo nechas vybrat nejsilnejsi) a zkontrolujes vysledek.
- **Reel se nerotuje** — vzdy sablona `metoda`. Zadny `reel-template.state.json`.
- **Story je jedna title-card**, ne 6 souboru.
- **Paleta je vyhrazena** — svetla klinicka (papir `#eef1f0`, smrk `#14201d`, evidence
  teal `#0e7c66`, signal `#c2402b`, tlumena `#7a8a85`). Retro pribehovou ani sportovni
  brandovou paletu metody NESMI pouzit — v feedu se maji odlisit svetlym pozadim.

## Vstup — tema z knihovne baze

Metodicke posty stoji na **content-engine** (Postgres + pgvector KB tvrzeni a temat).
Zneni se nepiše rucne, generuje ho prikaz `karusel`:

```bash
cd promo/content-engine
.venv/bin/python main.py karusel                 # nejsilnejsi tema napric KB
.venv/bin/python main.py karusel --sport run     # nejsilnejsi behecke tema
.venv/bin/python main.py karusel --topic-id 87   # konkretni tema
.venv/bin/python main.py karusel --topic-id 87 --dry-run   # jen vypis, nezapisuj
```

Prikaz vybere tema, nacte jeho tvrzeni, levny LLM z nich napise cesky text sedmi slidu
a zapiše `promo/metody/02-zneni/NNN-<slug>.md` (dalsi poradove cislo se odvodi automaticky).
Blok `## Fakta` se sestavi z odkazu tvrzeni deterministicky.

Vyber tema podle zadani uzivatele:

- konkretni tema, kdyz zna `--topic-id` (seznam: `main.py stats` / `main.py hledej "…"`),
- jinak `--sport run` pro nejsilnejsi behecke tema (default sport projektu je beh),
- `--dry-run` pouzij, kdyz chce uzivatel zneni jen videt a schvalit pred zapisem.

Pozor: prikaz potrebuje `.venv` content-engine (ma `pgvector`, `openai`) a `OPENAI_API_KEY`
v `promo/content-engine/.env`. Spousti se z `promo/content-engine/`.

## Render pipeline

Render prikazy (`render_metoda.py`, reel, story) spoustej z **korene projektu**
(`AI-trener`) pres `python3`. Bridge `karusel` z `promo/content-engine/` pres `.venv`.

### 1. Nacist kontext

- `promo/metody/00-nastaveni/metoda-ramec.md`
- `promo/metody/00-nastaveni/styl-metoda.md`
- pri renderu i `src/promo/metody/render_metoda.py`, kdyz si nejsi jisty argumenty

### 2. Vyrobit zneni z tematu

```bash
cd promo/content-engine
.venv/bin/python main.py karusel --topic-id <ID> --dry-run   # nahled
.venv/bin/python main.py karusel --topic-id <ID>             # zapis do 02-zneni
cd ../..
```

Zapamatuj si `NNN-<slug>` z vystupu — je to id noveho zneni. Zkontroluj, ze headliny
jsou konkretni vety (ne nazvy roli jako „Jak to funguje"), slide 4 ma cislo i dukaz a
`## Fakta` sedi.

### 3. Dry-run carouselu

```bash
python3 src/promo/metody/render_metoda.py --zneni NNN-<slug> --dry-run
```

Over, ze parser nasel 7 screenu, typy z katalogu (`hook`, `text`, `data`, `typo`),
slide `data` ma `Cislo:`/`Dukaz:` a `## Fakta` blok existuje. `render_metoda.py`
neznamy typ nebo dukaz odmitne a generovani zastavi.

### 4. Ukazkovy slide

```bash
python3 src/promo/metody/render_metoda.py --zneni NNN-<slug> --only 1
```

### 5. Dogenerovat carousel

```bash
python3 src/promo/metody/render_metoda.py --zneni NNN-<slug>
```

Vystup: `01-*.png` az `07-*.png` v rootu post slozky `promo/metody/03-posts/NNN-<slug>/`.

### 6. Reel (sablona metoda, tichy)

Reel skladej ze slidu hotoveho carouselu sdilenym generatorem. Metody jedou **vzdy**
profil `metoda` — nerotuj sablony. Protoze `render_reel_kinetic.py` resolvuje `--post`
proti `promo/pictures/`, pro metody predej **`--slides-dir`** (plna cesta k post slozce)
a **`--zneni`** (plna cesta ke zneni):

```bash
python3 src/promo/pictures/render_reel_kinetic.py \
  --slides-dir "promo/metody/03-posts/NNN-<slug>" \
  --template metoda \
  --zneni "promo/metody/02-zneni/NNN-<slug>.md"
```

Vystup `reel-kinetic-metoda.mp4` (`1080x1920`, tichy — trending audio se pridava az v IG
appce). Bez `--bpm` casuje skript delku slidu podle poctu znaku cteneho textu. `--bpm`
nezadavej — metodicke reely nesnapujeme na beat, data se ctou v klidu.

### 7. Story (jedna title-card)

```bash
python3 src/promo/metody/render_story_metoda.py --post NNN-<slug>
```

Vygeneruje jednu `story.png` (`1080x1920`) **primo v rootu postu**. Titulek bere z radku
`Story titulek:` ve zneni (fallback H1). Prepis lze pres `--title "..."`, poznamku nad
odkaz pres `--note "..."` (vychozi "Celá metoda v karuselu"). Spodni tretina zustava
volna — odkazovy sticker vklada uzivatel rucne v IG appce.

## Kontrola

- **carousel:** 7 finalnich PNG v rootu post slozky, rozmer `1080x1350`, svetla klinicka
  paleta (ne retro, ne sportovni), evidence odznak na slidu `data`, wordmark `trenzo.cz`
  vpravo dole,
- **reel:** existuje `reel-kinetic-metoda.mp4`, format `1080x1920`, tichy,
- **story:** jedna `story.png` v rootu postu, rozmer `1080x1920`, titulek rekne o CEM
  metoda je, spodni tretina volna na sticker,
- headliny jsou konkretni vety, ne nazvy roli,
- slide `data` nese cislo i uroven dukazu, `## Fakta` ma zdroje ke vsem tvrzenim,
- ceska diakritika v obrazku neni rozbita (over vizualne otevrenim PNG).

## Report

Na konci rekni:

- ktere tema KB (`--topic-id` + titulek) poslouzilo a jake `NNN-<slug>` zneni vzniklo,
- jake soubory vznikly (carousel `01-07`, `reel-kinetic-metoda.mp4`, `story.png`) a kam,
- jaky titulek story dostala,
- jestli prosla kontrola rozmeru, palety, evidence odznaku a diakritiky,
- pokud neco neproslo, navrhni jednu cilenou dalsi iteraci (napr. jine tema, uprava zneni).
