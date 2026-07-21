---
name: post-ig
description: "Vygeneruje Instagram obsah pro AI-trener podle lokalni pipeline v promo/pictures/: carousel (render_carousel.py), reel (render_reel.py) a story (gen_stories.py + render_story.py --simple). Postup: 01-myslenka -> 02-zneni podle metody -> dry-run -> ukazka -> finalni post do 03-posts/NN-nazev."
---

# Post IG

Pouzivej pouze aktualni lokalni pipeline projektu `AI-trener` v adresari
`promo/pictures/`. Skripty jsou v `promo/pictures/src/`.

Zdroj pravdy pro workflow je:

- `promo/pictures/README.md`
- `promo/pictures/00-nastaveni/metoda-transkript-carousel.md`
- `promo/pictures/src/render_carousel.py`

Skill umi tri druhy vystupu do stejne post slozky:

- **carousel** — `render_carousel.py` (slidy `1080x1350`)
- **reel** — `render_reel.py` (`reel.mp4` `1080x1920`)
- **story** — `gen_stories.py` (napise 2 story) + `render_story.py --simple`
  (jedno fotorealisticke story `1080x1920`, text vypaleny pres foto zaber)

## Vstupy

Pracuj s jednim z techto vstupu:

- myslenka: `promo/pictures/01-myslenka/<id>-<slug>.md`
- hotove zneni: `promo/pictures/02-zneni/<id>-<slug>.md`
- volne tema nebo transkriptovy extrakt od uzivatele

Pokud uzivatel doda myslenku, tema nebo extrakt, nejdriv vytvor nebo
pregeneruj odpovidajici soubor:

`promo/pictures/02-zneni/<id>-<slug>.md`

## Zneni

Zneni vzdy vytvor podle:

`promo/pictures/00-nastaveni/metoda-transkript-carousel.md`

Soubor `02-zneni` ma obsahovat:

- puvodni extrakt,
- slib carouselu,
- logickou mapu,
- povinny radek `Kategorie: A` nebo `Kategorie: P` pod titulkem (bez nej
  `render_carousel.py` odmitne generovat),
- `## Carousel`,
- pozy/vyrazy avatara u kazdeho screenu,
- `## Simple carousel`, pokud je potreba zkracena renderovaci verze,
- popisek,
- redakcni doplneni.

Pro render plati:

- `render_carousel.py` preferuje `## Simple carousel`, pokud existuje.
- Jinak pouzije `## Carousel`.
- Kazdy screen ma mit maximalne 2 vety.
- `Póza:` nebo `Poza:` pod screenem ridi avatar.
- `Zvýraznit:` ridi presna slova pro lime/electric-blue highlight.
- Cisla nemen bez opory ve zdroji; doplnky oznac v redakcni casti.

## Render pipeline

Skripty jsou v `promo/pictures/src/` a skladaji tri oddelene zdroje pravdy:

- styl: `promo/pictures/00-nastaveni/styl.md`
- identita avatara: `promo/pictures/00-nastaveni/avatar/base3_reencoded.png` defaultne
- obsah: `promo/pictures/02-zneni/<id>-<slug>.md`

Vystup se uklada do:

`promo/pictures/03-posts/NN-<A|P>-<slug-bez-zdrojoveho-id>/`

Uvnitř:

- `01-*.png` az `0x-*.png` — finalni carousel PNG `1080x1350`
- `story-*.png` / `story-simple.png` — finalni story PNG `1080x1920`
- `raw/` — neorezane originaly z image modelu (`raw/stories/` pro story)
- `popisek.md` — popisek exportovany ze sekce `## Popisek`
- `reel.mp4` — tichy IG Reel slideshow `1080x1920` po spusteni `render_reel.py`

## Povinne kroky (carousel)

### 1. Nacist kontext

Pred praci nacti relevantni soubory:

- `promo/pictures/README.md`
- `promo/pictures/00-nastaveni/metoda-transkript-carousel.md`
- vstupni `01-myslenka` nebo `02-zneni`
- pri renderu i `promo/pictures/src/render_carousel.py`, pokud si nejsi jisty argumenty

### 2. Pripravit zneni

Vytvor nebo uprav `02-zneni/<id>-<slug>.md` podle metody. Zachovej jednu hlavni
myslenku. Neslucuj vice metod do jednoho zmateneho postupu.

### 3. Spustit dry-run

Pred generovanim obrazku vzdy spust dry-run:

```powershell
python .\promo\pictures\src\render_carousel.py --zneni <id>-<slug> --dry-run
```

Zkontroluj, ze parser nasel spravny pocet screenu, headline, supporting line,
highlight a pozy.

### 4. Vyrenderovat ukazkovy slide

Kdyz uzivatel chce ukazku nebo kdyz se vytvari novy post, nejdriv renderuj jen
jeden slide:

```powershell
python .\promo\pictures\src\render_carousel.py --zneni <id>-<slug> --avatar base3_reencoded --only 1
```

Defaultni backend je `codex`; pouzij ho, pokud uzivatel neurci jinak.

### 5. Dogenerovat carousel

Po schvaleni ukazky nebo pri jasnem pozadavku na finalni post dogeneruj vse:

```powershell
python .\promo\pictures\src\render_carousel.py --zneni <id>-<slug> --avatar base3_reencoded
```

Placeny API backend pouzij jen kdyz to uzivatel explicitne chce nebo kdyz je
potreba srovnani kvality/rychlosti:

```powershell
python .\promo\pictures\src\render_carousel.py --zneni <id>-<slug> --avatar base3_reencoded --backend api
```

### 6. Vyrenderovat Reel

Po hotovem carouselu sloz IG Reel do stejne post slozky:

```powershell
python .\promo\pictures\src\render_reel.py --post 03-posts/NN-<A|P>-<slug-bez-zdrojoveho-id>
```

## Story (gen_stories + render_story --simple)

Story je samostatna upoutavka na hotovy post + reel. Bezi ve dvou krocich a
zamerne pouziva **oba** skripty — `gen_stories.py` napise text, `render_story.py
--simple` z nej udela jeden fotorealisticky obrazek.

### Krok A — text (`gen_stories.py`)

GPT ze zneni napise `stories.md` se **VZDY dvema** story: story 1 = chytlavy
souhrn celeho carouselu, story 2 = CTA na post + reel. Zapise se do post slozky.

```powershell
python .\promo\pictures\src\gen_stories.py --zneni <id>-<slug> --dry-run
python .\promo\pictures\src\gen_stories.py --zneni <id>-<slug>
```

Nejdriv `--dry-run` (ukaze prompt + vybrane lokace, nic nezapisuje), pak ostry
beh. Vystup je `stories.md` v `03-posts/NN-.../`.

### Krok B — vyber zaberu (`pick_scene.py`)

Fotku pro simple story **nevybiraj rucne ani "podle citu"** — svadi to porad na
les (je v 5 z 9 scen). Vyber deleguj na `pick_scene.py`, ktery garantuje
rozmanitost: losuje lokaci uniformne (les/mesto/posilovna/stadion maji stejnou
sanci) a drzi recency log, takze dve story po sobe nemaji stejne prostredi.

Tvoje (skillova) uloha je jen urcit **uhel zaberu podle pozy** 1. story a predat
ho jako `--pohled`. Dostupne pohledy: `beh-zepredu`, `beh-zezadu`,
`detail-doslapu`, `detail-hodinek`, `pohled-na-hodinky`, `popadnuti-dechu`,
`sed-s-telefonem`, `stoj-zepredu`. Kdyz poza nesedi na zadny konkretni, pusť
`pick_scene.py` bez `--pohled` (vybere ze vsech).

```powershell
# nejdriv nahled bez zapisu do logu (over lokaci):
python .\promo\pictures\src\pick_scene.py --pohled pohled-na-hodinky --dry-run
# ostry vyber (zapise do recency logu, vypise cestu k PNG na stdout):
python .\promo\pictures\src\pick_scene.py --pohled pohled-na-hodinky
```

Skript vypise cestu k PNG na stdout (info o vyberu jde na stderr). Tu cestu
predej do render_story.

### Krok C — obrazek (`render_story.py --simple`)

Simple rezim vypali text **1. story** ze `stories.md` pres vybrany fotorealisticky
zaber pres PIL — jeden deterministicky obrazek `story-simple.png`, zadny AI model,
zadna cena. Text si render_story najde sam (1. story ze `stories.md`); foto mu
predas pres `--image` z kroku B.

```powershell
python .\promo\pictures\src\render_story.py --stories <id>-<slug> --simple --image <cesta-z-pick_scene>
```

Kompletni AI story pipeline (funnel poll/quiz/reveal/cta, vic obrazku, brand
razitko, `publikace-stories.md` navod) zustava dostupna bez `--simple` — pouzij
ji jen kdyz uzivatel chce plnohodnotny vicedilny story funnel, ne rychlou simple
upoutavku.

## Kontrola

Pred reportem zkontroluj:

- **carousel:** finalni PNG primo v rootu post slozky, rozmer `1080x1350`,
  odpovidajici original ve `raw/`,
- **story:** `story-simple.png` v rootu post slozky, rozmer `1080x1920`,
- existuje `popisek.md` (u carouselu),
- existuje `reel.mp4` a ma format `1080x1920` (pokud se delal reel),
- headline a supporting line odpovidaji `02-zneni` (carousel) resp. 1. story
  ze `stories.md` (simple story),
- ceska diakritika v obrazku neni rozbita,
- avatar/foto odpovida ocekavani,
- text neprekryva oblicej ani hlavni vizualni detail.

Diakritiku over vizualne otevrenim finalniho PNG. Text je vypaleny v obrazku,
takze samotny textovy soubor nestaci.

## Report

Na konci rekni:

- ktery soubor `02-zneni` (a u story i `stories.md`) byl vytvoren nebo upraven,
- jake PNG / mp4 vznikly (carousel / story / reel),
- kam byly ulozeny,
- u simple story ktery foto zaber (`--image`) byl pouzity,
- jestli prosla kontrola rozmeru a diakritiky,
- pokud neco neproslo, navrhni jednu cilenou dalsi iteraci.
