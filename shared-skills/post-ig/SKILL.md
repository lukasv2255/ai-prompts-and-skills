---
name: post-ig
description: "Vygeneruje Instagram obsah pro AI-trener podle lokalni pipeline v src/promo/pictures/: carousel (render_carousel.py), reel (render_reel_kinetic.py, 3 sablony s rotaci) a story (gen_stories.py -> render_story.py: 6 souboru = story-01-souhrn + story-02-cta pres codex + story-simple-left/right + story-simple-bg + story-simple-text pres --simple). Postup: 01-myslenka -> 02-zneni podle metody -> dry-run -> ukazka -> finalni post do 03-posts/NN-nazev."
---

# Post IG

Pouzivej pouze aktualni lokalni pipeline projektu `AI-trener`. Assety (styl,
avatar, myslenky, zneni, posty) jsou v `promo/pictures/`, **skripty** jsou v
`src/promo/pictures/`.

Zdroj pravdy pro workflow je:

- `promo/pictures/README.md`
- `promo/pictures/00-nastaveni/metoda-transkript-carousel.md`
- `src/promo/pictures/render_carousel.py`

Skill umi tri druhy vystupu do stejne post slozky:

- **carousel** — `render_carousel.py` (slidy `1080x1350`)
- **reel** — `render_reel_kinetic.py` (`reel-kinetic*.mp4` `1080x1920`, 3 sablony
  s automatickou rotaci)
- **story** — 6 souboru: `gen_stories.py` (napise 2 story) + `render_story.py`
  (normalni rezim, codex -> `story-01-souhrn.png` hook + `story-02-cta.png`) +
  `pick_scene.py` (vybere zaber s rotaci prostredi) + `render_story.py --simple`
  (fotorealisticke varianty `story-simple-left.png` / `story-simple-right.png`
  - `story-simple-bg.png` cisty zaber + `story-simple-text.png` transparentni text
    s efektem k rucnimu vrstveni)

## State soubory (rotace)

Aby se sablony reelu a prostredi story neopakovaly, drzime maly rotacni stav
**hned vedle skriptu** v `src/promo/pictures/`:

- `src/promo/pictures/reel-template.state.json` — posledni pouzita sablona reelu.
- `src/promo/pictures/.recent-scenes.json` — recency log lokaci simple story
  (vede si ho sam `pick_scene.py`).
- `src/promo/pictures/.recent-story-locations.json` — recency log lokaci pozadi
  AI story 1 (vede si ho sam `gen_stories.py`).
- `src/promo/pictures/.avatar-bag.json` — zbytek "pytliku" avataru (vede si ho
  sam `pick_avatar.py`).

Vsechny soubory vznikaji az za behu; do gitu je commitovat nemusis.

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

Skripty jsou v `src/promo/pictures/` a skladaji tri oddelene zdroje pravdy:

- styl: `promo/pictures/00-nastaveni/styl.md`
- identita avatara: `promo/pictures/00-nastaveni/avatar/<jmeno>.png` — vybira
  `pick_avatar.py`, viz nize
- obsah: `promo/pictures/02-zneni/<id>-<slug>.md`

Vystup se uklada do:

`promo/pictures/03-posts/NN-<A|P>-<slug-bez-zdrojoveho-id>/`

Uvnitř:

- `01-*.png` az `0x-*.png` — finalni carousel PNG `1080x1350`
- `story-simple-left.png` / `story-simple-right.png` — dve varianty simple story
  `1080x1920` (finalni si vybere uzivatel)
- `story-simple-bg.png` — cisty foto zaber `1080x1920` bez textu (k vrstveni)
- `story-simple-text.png` — transparentni text 1. story s efektem (glow + speed
  streaks), realna alfa a kryci pismena — k navrstveni pres video/foto v editoru
- `raw/` — neorezane originaly z image modelu (`raw/stories/` pro story)
- `popisek.md` — popisek exportovany ze sekce `## Popisek`
- `reel-kinetic*.mp4` — tichy IG Reel `1080x1920` po spusteni `render_reel_kinetic.py`

Prikazy spoustej z korene projektu (`AI-trener`).

## Avatar — rotace (`--avatar` NEZADAVAT)

Avatara vybira `pick_avatar.py` sam. Drzi "pytlik" peti kusu
(`2x original, 2x bryle, 1x mikina`), takze kazda petice postu ma garantovany
pomer 2:2:1 v nahodnem poradi. Jednotka je **post**, ne slide — cely carousel
dostane jednoho avatara a osoba se uprostred neprevleka.

**Prepinac `--avatar` do prikazu nepridavej.** Rotace se aktivuje jen tehdy,
kdyz `--avatar` chybi; jakmile ho zadas, pytlik se obejde a posty budou porad
se stejnou osobou. Zadej ho jen kdyz uzivatel vyslovne rekne konkretniho avatara.

Aktualne dostupni avatari jsou pouze `original`, `bryle`, `mikina`
(`00-nastaveni/avatar/*.png`); zbytek je v `avatar/nepouzivane/`. Jmena si
neodhaduj z pameti — kdyz uzivatel chce konkretniho, over si `ls` v te slozce.

Stav pytliku prohlednes bez zasahu:

```bash
python src/promo/pictures/pick_avatar.py --status
```

Rozdelany post si vybraneho avatara pamatuje v sidecaru `.avatar` ve sve slozce,
takze pozdejsi `--only` re-render dostane stejnou osobu jako zbytek carouselu.

## Povinne kroky (carousel)

### 1. Nacist kontext

Pred praci nacti relevantni soubory:

- `promo/pictures/README.md`
- `promo/pictures/00-nastaveni/metoda-transkript-carousel.md`
- vstupni `01-myslenka` nebo `02-zneni`
- pri renderu i `src/promo/pictures/render_carousel.py`, pokud si nejsi jisty argumenty

### 2. Pripravit zneni

Vytvor nebo uprav `02-zneni/<id>-<slug>.md` podle metody. Zachovej jednu hlavni
myslenku. Neslucuj vice metod do jednoho zmateneho postupu.

### 3. Spustit dry-run

Pred generovanim obrazku vzdy spust dry-run:

```bash
python src/promo/pictures/render_carousel.py --zneni <id>-<slug> --dry-run
```

Zkontroluj, ze parser nasel spravny pocet screenu, headline, supporting line,
highlight a pozy.

### 4. Vyrenderovat ukazkovy slide

Kdyz uzivatel chce ukazku nebo kdyz se vytvari novy post, nejdriv renderuj jen
jeden slide:

```bash
python src/promo/pictures/render_carousel.py --zneni <id>-<slug> --only 1
```

Defaultni backend je `codex`; pouzij ho, pokud uzivatel neurci jinak.
`--only` pytlik avataru neposouva (jen nahlizi), takze ukazkovy slide rotaci
nespotrebuje.

### 5. Dogenerovat carousel

Po schvaleni ukazky nebo pri jasnem pozadavku na finalni post dogeneruj vse:

```bash
python src/promo/pictures/render_carousel.py --zneni <id>-<slug>
```

Placeny API backend pouzij jen kdyz to uzivatel explicitne chce nebo kdyz je
potreba srovnani kvality/rychlosti:

```bash
python src/promo/pictures/render_carousel.py --zneni <id>-<slug> --backend api
```

### 6. Vyrenderovat Reel (kinetic, s rotaci sablon)

Reel skladej **novym kinetic generatorem** `render_reel_kinetic.py` ze slidu
hotoveho carouselu. Ma tri sablony (`-t`), popis viz
`docs/promo/reels/sablony-popis.md`:

| Sablona | Vystup                   | Charakter                                   |
| ------- | ------------------------ | ------------------------------------------- |
| `calm`  | `reel-kinetic.mp4`       | vychozi zamcene optimum, edukativni, klidny |
| `punch` | `reel-kinetic-punch.mp4` | energicka / TikTok, swipe, silnejsi grain   |
| `clean` | `reel-kinetic-clean.mp4` | premium, bez swipu, modry progress bar      |

**Sablonu nevybiraj nahodne — rotuj cyklicky** `calm -> punch -> clean -> calm`.
Stav drzi `src/promo/pictures/reel-template.state.json` ve formatu `{"last": "<sablona>"}`:

1. Precti soubor. Kdyz neexistuje nebo je nevalidni, ber posledni jako `clean`
   (aby prvni beh zacal na `calm`).
2. Dalsi sablona = nasledujici v poradi `["calm","punch","clean"]` (za `clean`
   opet `calm`).
3. Vyrenderuj s vybranou sablonou.
4. Zapis zpet `{"last": "<pouzita sablona>"}`.

Kdyz uzivatel explicitne rekne konkretni sablonu, pouzij ji a stav stejne aktualizuj.

```bash
python src/promo/pictures/render_reel_kinetic.py --post 03-posts/NN-<A|P>-<slug> -t <sablona> --bpm 120 --auto-beats
```

`--auto-beats` casuje slidy podle mnozstvi textu (cte ze zneni / `popisek.md`) a
**vyzaduje `--bpm`** (delky se snapuji na doby; 120 je rozumny default).
Popis dalsich prepinacu (`--bpm`, `--music`, `--no-bar`...) je v
`docs/promo/reels/reels-generator-a-sablony.md`.

## Story (gen_stories + render_story: 4 soubory)

Story je samostatna upoutavka na hotovy post + reel. Vystup je **VZDY 6 PNG**
`1080x1920` v post slozce:

- `story-01-souhrn.png` — hook, avatar postaveny do prostredi lokace (AI render, codex)
- `story-02-cta.png` — CTA na post + reel (AI render, codex)
- `story-simple-left.png` / `story-simple-right.png` — hook vypaleny pres
  fotorealisticky zaber (PIL, zdarma), dve varianty podle strany postavy
- `story-simple-bg.png` — cisty foto zaber bez textu (k rucnimu vrstveni)
- `story-simple-text.png` — transparentni text 1. story s efektem (glow + speed
  streaks), realna alfa + kryci pismena (k navrstveni pres video/foto v editoru)

Prvni dva jdou z `gen_stories.py` -> `render_story.py` (normalni rezim), zbyle
ctyri z `render_story.py --simple` (dve vypalene varianty + cisty zaber + text
overlay). Bezi ve ctyrech krocich.

### Krok A — text (`gen_stories.py`)

GPT ze zneni napise `stories.md` se **VZDY dvema** story: story 1 = chytlavy
souhrn celeho carouselu (pole `Obrázek:` miri na cistou fotku lokace), story 2 =
CTA na post + reel. Zapise se do post slozky.

**Lokaci pozadi story 1 losuje `gen_stories.py` sam nahodne** (uniformne pres
slozky v `00-nastaveni/scena/`) s recency logem
`.recent-story-locations.json` — GPT do vyberu lokace nemluvi (mel tendenci vracet
porad les). Kdyz chces konkretni prostredi (napr. stadion), preber vyber rucne:
uprav radek `Obrázek:` ve `stories.md` a spust jen Krok B s `--only 1`.

```bash
python src/promo/pictures/gen_stories.py --zneni <id>-<slug> --dry-run
python src/promo/pictures/gen_stories.py --zneni <id>-<slug>
```

Nejdriv `--dry-run` (ukaze prompt + vybrane lokace, nic nezapisuje), pak ostry
beh. Vystup je `stories.md` v `03-posts/NN-.../`.

### Krok B — AI render hook + CTA (`render_story.py`, codex)

Normalni rezim (bez `--simple`) precte `stories.md` a vyrenderuje **obe** story
pres codex (ChatGPT plan, zdarma): story 1 ma pole `Obrázek:` -> avatar postaveny
do ilustrovaneho prostredi lokace (`story-01-souhrn.png`), story 2 je typ `cta` ->
standardni brand story (`story-02-cta.png`). Vyzaduje **codex CLI**
(`npm install -g @openai/codex`, prihlaseni pres ChatGPT); bez nej jede jen placeny
`--backend api`.

**DULEZITE — predej PLNOU cestu ke `stories.md`**, ne `<id>-<slug>`. `gen_stories.py`
v Kroku A vypise presnou cestu (`03-posts/NN-.../stories.md`); pouzij ji. Kdyby ses
spolehnul na `--stories <id>`, `resolve_stories` prohledava `04-drafts/` PRED
`03-posts/`, takze stejnojmenny stary draft by prebil cerstvy vystup.

```bash
python src/promo/pictures/render_story.py --stories 03-posts/NN-<A|P>-<slug>/stories.md
```

### Krok C — vyber zaberu / pozy (`pick_scene.py`)

Fotku pro simple story **nevybiraj rucne ani "podle citu"** — svadi to porad na
les (je v 5 z 9 scen). Vyber deleguj na `pick_scene.py`, ktery garantuje
rozmanitost: losuje lokaci uniformne (les/mesto/posilovna/stadion maji stejnou
sanci) a drzi recency log `src/promo/pictures/.recent-scenes.json` (posledni 2
lokace se vyradi), takze dve story po sobe nemaji stejne prostredi. Tim je
"rotace pozy" resena skriptem — ty jen urcis nejvhodnejsi uhel.

Tvoje (skillova) uloha je urcit **uhel zaberu podle pozy** 1. story a predat
ho jako `--pohled`. Dostupne pohledy: `beh-zepredu`, `beh-zezadu`,
`detail-doslapu`, `detail-hodinek`, `pohled-na-hodinky`, `popadnuti-dechu`,
`sed-s-telefonem`, `stoj-zepredu`. Kdyz poza nesedi na zadny konkretni, pusť
`pick_scene.py` bez `--pohled` (vybere ze vsech).

```bash
# nejdriv nahled bez zapisu do logu (over lokaci):
python src/promo/pictures/pick_scene.py --pohled pohled-na-hodinky --dry-run
# ostry vyber (zapise do recency logu, vypise cestu k PNG na stdout):
python src/promo/pictures/pick_scene.py --pohled pohled-na-hodinky
```

Skript vypise cestu k PNG na stdout (info o vyberu jde na stderr). Tu cestu
predej do render_story.

### Krok D — simple hook pres foto (`render_story.py --simple`)

Simple rezim vypali text **1. story** ze `stories.md` pres vybrany fotorealisticky
zaber pres PIL — deterministicke obrazky, zadny AI model, zadna cena. Protoze z
fotky nejde spolehlive urcit, na ktere strane stoji postava, vygeneruji se **obe
varianty**: `story-simple-left.png` (text vlevo) i `story-simple-right.png` (text
vpravo). Uzivatel vybere tu, kde text **nekryje postavu**. Stejna PLNA cesta ke
`stories.md` jako v Kroku B.

Navic `--simple` ulozi dva soubory k rucnimu vrstveni v editoru (CapCut): cisty
foto zaber bez textu `story-simple-bg.png` a transparentni text s efektem
`story-simple-text.png` (glow + speed streaks, realna alfa, kryci pismena). Text
pak lze navrstvit primo pres reel video nebo jiny zaber.

```bash
python src/promo/pictures/render_story.py --stories 03-posts/NN-<A|P>-<slug>/stories.md --simple --image <cesta-z-pick_scene>
```

Po Krocich A–D ma post slozka vsech **6 story souboru**. `--simple` renderuje
jen story 1 (hook, vcetne bg + text overlay); CTA obrazek (`story-02-cta.png`)
dela Krok B.

## Kontrola

Pred reportem zkontroluj:

- **carousel:** finalni PNG primo v rootu post slozky, rozmer `1080x1350`,
  odpovidajici original ve `raw/`,
- **reel:** existuje `reel-kinetic*.mp4` odpovidajici pouzite sablone a ma format
  `1080x1920`,
- **story:** vsech **6 souboru** v rootu post slozky, rozmer `1080x1920` —
  `story-01-souhrn.png`, `story-02-cta.png`, `story-simple-left.png`,
  `story-simple-right.png`, `story-simple-bg.png` (RGB, bez alfy),
  `story-simple-text.png` (RGBA, pruhledne pozadi + kryci pismena),
- existuje `popisek.md` (u carouselu),
- headline a supporting line odpovidaji `02-zneni` (carousel) resp. 1. story
  ze `stories.md` (simple story),
- ceska diakritika v obrazku neni rozbita,
- avatar/foto odpovida ocekavani a nebyl vnucen pres `--avatar` (rotace bezi),
- text neprekryva oblicej ani hlavni vizualni detail (u story porovnej obe strany).

Diakritiku over vizualne otevrenim finalniho PNG. Text je vypaleny v obrazku,
takze samotny textovy soubor nestaci.

## Report

Na konci rekni:

- ktery soubor `02-zneni` (a u story i `stories.md`) byl vytvoren nebo upraven,
- jake PNG / mp4 vznikly (carousel / story / reel),
- kam byly ulozeny,
- u reelu **kterou sablonu** rotace vybrala a na jakou se posunul stav,
- u story ze 6 souboru: ze `story-01-souhrn.png` + `story-02-cta.png` vznikly
  pres codex a ze `story-simple-left/right.png` + `story-simple-bg.png` +
  `story-simple-text.png` pres `--simple` (a ktery foto zaber `--image` +
  `--pohled` byl pouzity),
- jestli prosla kontrola rozmeru a diakritiky,
- pokud neco neproslo, navrhni jednu cilenou dalsi iteraci.
