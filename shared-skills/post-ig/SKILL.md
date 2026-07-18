---
name: post-ig
description: "Vygeneruje Instagram carousel pro AI-trener podle lokalni pipeline: 01-myslenka -> 02-zneni podle metody -> dry-run render_carousel.py -> ukazkovy slide -> finalni post do 03-posts/NN-nazev."
---

# Post IG

Pouzivej pouze aktualni lokalni pipeline projektu `AI-trener` v adresari
`promo/ig/`.

Zdroj pravdy pro workflow je:

- `promo/ig/README.md`
- `promo/ig/00-nastaveni/metoda-transkript-carousel.md`
- `promo/ig/render_carousel.py`

## Vstupy

Pracuj s jednim z techto vstupu:

- myslenka: `promo/ig/01-myslenka/<id>-<slug>.md`
- hotove zneni: `promo/ig/02-zneni/<id>-<slug>.md`
- volne tema nebo transkriptovy extrakt od uzivatele

Pokud uzivatel doda myslenku, tema nebo extrakt, nejdriv vytvor nebo
pregeneruj odpovidajici soubor:

`promo/ig/02-zneni/<id>-<slug>.md`

## Zneni

Zneni vzdy vytvor podle:

`promo/ig/00-nastaveni/metoda-transkript-carousel.md`

Soubor `02-zneni` ma obsahovat:

- puvodni extrakt,
- slib carouselu,
- logickou mapu,
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

Renderuj pouze pres:

`promo/ig/render_carousel.py`

Skript sklada tri oddelene zdroje pravdy:

- styl: `promo/ig/00-nastaveni/styl.md`
- identita avatara: `promo/ig/00-nastaveni/avatar/base3_reencoded.png` defaultne
- obsah: `promo/ig/02-zneni/<id>-<slug>.md`

Skript vystup uklada do:

`promo/ig/03-posts/NN-<slug-bez-zdrojoveho-id>/`

Uvnitř:

- `01-*.png` az `0x-*.png` — finalni carousel PNG `1080x1350`
- `story-*.png` — finalni story PNG `1080x1920`
- `raw/` — neorezane originaly z image modelu
- `popisek.md` — popisek exportovany ze sekce `## Popisek`
- `reel.mp4` — tichy IG Reel slideshow `1080x1920` po spusteni `render_reel.py`

## Povinne kroky

### 1. Nacist kontext

Pred praci nacti relevantni soubory:

- `promo/ig/README.md`
- `promo/ig/00-nastaveni/metoda-transkript-carousel.md`
- vstupni `01-myslenka` nebo `02-zneni`
- pri renderu i `promo/ig/render_carousel.py`, pokud si nejsi jisty argumenty

### 2. Pripravit zneni

Vytvor nebo uprav `02-zneni/<id>-<slug>.md` podle metody. Zachovej jednu hlavni
myslenku. Neslucuj vice metod do jednoho zmateneho postupu.

### 3. Spustit dry-run

Pred generovanim obrazku vzdy spust dry-run:

```powershell
python .\promo\ig\render_carousel.py --zneni <id>-<slug> --dry-run
```

Zkontroluj, ze parser nasel spravny pocet screenu, headline, supporting line,
highlight a pozy.

### 4. Vyrenderovat ukazkovy slide

Kdyz uzivatel chce ukazku nebo kdyz se vytvari novy post, nejdriv renderuj jen
jeden slide:

```powershell
python .\promo\ig\render_carousel.py --zneni <id>-<slug> --avatar base3_reencoded --only 1
```

Defaultni backend je `codex`; pouzij ho, pokud uzivatel neurci jinak.

### 5. Dogenerovat carousel

Po schvaleni ukazky nebo pri jasnem pozadavku na finalni post dogeneruj vse:

```powershell
python .\promo\ig\render_carousel.py --zneni <id>-<slug> --avatar base3_reencoded
```

Placeny API backend pouzij jen kdyz to uzivatel explicitne chce nebo kdyz je
potreba srovnani kvality/rychlosti:

```powershell
python .\promo\ig\render_carousel.py --zneni <id>-<slug> --avatar base3_reencoded --backend api
```

### 6. Vyrenderovat Reel

Po hotovem carouselu sloz IG Reel do stejne post slozky:

```powershell
python .\promo\ig\render_reel.py --post 03-posts/NN-<slug-bez-zdrojoveho-id>
```

## Kontrola

Pred reportem zkontroluj:

- existuji finalni PNG primo v rootu post slozky,
- finalni PNG ma `1080x1350`,
- existuje odpovidajici original ve `raw/`,
- existuje `popisek.md`,
- existuje `reel.mp4` a ma format `1080x1920`,
- headline a supporting line odpovidaji `02-zneni`,
- ceska diakritika v obrazku neni rozbita,
- avatar odpovida aktualni referenci,
- text neprekryva oblicej ani hlavni vizualni detail.

Diakritiku over vizualne otevrenim finalniho PNG. Text je vypaleny v obrazku,
takze samotny textovy soubor nestaci.

## Report

Na konci rekni:

- ktery soubor `02-zneni` byl vytvoren nebo upraven,
- jake PNG vznikly,
- kam byly ulozeny,
- jestli prosla kontrola rozmeru a diakritiky,
- pokud neco neproslo, navrhni jednu cilenu dalsi iteraci.
