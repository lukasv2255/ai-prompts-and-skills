---
name: post-ig-pribeh
description: "Vygeneruje Instagram obsah pro PRIBEHOVE (historicke) posty AI-trener podle pipeline v src/promo/pribehy/: carousel (render_pribeh.py, 7 slidu, styl-plate misto avatara), reel (render_reel_kinetic.py -t archiv, tichy) a story (render_story_pribeh.py -> jedna title-card story.png primo v rootu postu). Davkovy rezim pro stovku temat: nejdriv vsechna zneni, pak jazykova kontrola, teprve pak jeden beh fronty. Postup: zasobnik-temat.md -> 01-myslenka -> 02-zneni podle pribeh-ramec.md -> zkontroluj_zneni.py -> fronta_render.py -> 03-posts/NNN-slug."
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
- `promo/pribehy/00-nastaveni/zasobnik-temat.md` — 100 temat, u kazdeho uhel a obraz
- `src/promo/pribehy/render_pribeh.py`

Skill umi tri druhy vystupu do stejne post slozky `promo/pribehy/03-posts/NNN-<slug>/`:

- **carousel** — `render_pribeh.py` (7 slidu `1080x1350`, styl-plate + dobova fotka
  jako predloha, zadny avatar, zadne brandove razitko)
- **reel** — `render_reel_kinetic.py -t archiv` (`reel-kinetic-archiv.mp4` `1080x1920`,
  tichy, inkoustovy ramecek + rezavy progress bar, **bez rotace sablon** — pribehy
  jedou vzdy `archiv`, tvrdy strop 25 s)
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

---

# Davkovy rezim (vychozi pro stovku temat)

Pipeline ma **tri faze a nesmi se michat**. Duvod je cena chyby: karusel stoji ~20
minut strojoveho casu, takze najit spatnou vetu az na hotovem obrazku znamena hodinu
zpatky. Nejdriv se tedy napise vsechno, co je levne opravit (text), pak se to precte,
a teprve pak se pousti to drahe (render).

| Faze  | Co se dela                  | Cim se konci                       |
| ----- | --------------------------- | ---------------------------------- |
| **1** | napsat vsechna zneni        | `zkontroluj_zneni.py` bez chyb     |
| **2** | precist je kvuli smyslu vet | opravena zneni, znovu bez chyb     |
| **3** | jeden beh renderu           | `fronta_render.py --stav` samy ✓✓✓ |

**Do faze 3 se nesmi vstoupit s neopravenym zneni.** Fronta nic nekontroluje, ta jen
generuje.

## Faze 1 — napsat vsechna zneni

Temata ber ze `zasobnik-temat.md` po blocich (A–I), ne na preskacku. Zasobnik ma
u kazdeho tematu uhel pro Trenzo, sloupec _Fakta_ (jestli je podklad po ruce) a
sloupec _Obraz_ (co hledat v katalogu predloh).

Pro kazde tema vznikaji **dva soubory**:

1. `01-myslenka/<NNN>-<slug>.md` — reserse: myslenka, proc to sem patri, zdroje
   a povinny blok `## Poznámka k rešerši` s tim, co se do zneni **nedostalo a proc**
   (nedolozitelne legendy, netvrzena kauzalita, detaily patrici k jinemu tematu).
2. `02-zneni/<NNN>-<slug>.md` — samotne zneni podle `pribeh-ramec.md`.

Davky delej po **5–8 tematech** a po kazde davce pust kontrolu. Vic naraz se
nevyplati: chyba v pochopeni ramce se pak opravuje na dvaceti souborech misto na peti.

Reserse se da paralelizovat subagenty (jeden agent = jedno tema, pise oba soubory).
Predlohy si kazdy agent hleda sam:

```bash
python3 src/promo/pribehy/katalog_predloh.py --find <tagy> --od <rok> --do <rok>
```

Katalog vypise rovnou radky `Předloha:` a `Licence:` k vlozeni do zneni. **Nehledej
predlohy rucne na Commons** — katalog uz ma vyresene, ze snimek je volny i v EU.

Po kazde davce:

```bash
python3 src/promo/pribehy/zkontroluj_zneni.py
```

## Faze 2 — jazykova kontrola

Parser hlida strukturu, ne smysl. Nesmyslna slovni spojeni, kostrbate vety a
opakujici se obraty najde jen cteni. Report je od toho, aby se sto zneni dalo precist
najednou misto otevirani sta souboru:

```bash
python3 src/promo/pribehy/zkontroluj_zneni.py --texty tmp/kontrola-textu.md
```

Vypise pro kazde zneni sedm headlinu s podtitulky a zvyraznenim pod sebou. Cti
a hledej:

- **nesmyslna nebo prehnana slovni spojeni** — hlavne v headlinech, kde se skrtalo
  kvuli delce,
- **opakujici se formulace napric tematy** (stejny obrat v peti pointach = feed zni
  jako sablona),
- **headline, ktery bez podtitulku nedava smysl** — na slidu je vetsi a cte se prvni,
- **cislo v headlinu, ktere neni v `## Fakta`** (parser hlida jen letopocty, ne
  procenta a casy),
- **pointu, ktera netvrdi nic** — slide 7 musi prevest historii na dnesek.

Opravy pis primo do `02-zneni/`. Na konci faze musi `zkontroluj_zneni.py` projit bez
chyb a report se musi dat precist bez zadrhnuti.

## Faze 3 — jeden beh renderu

```bash
python3 src/promo/pribehy/fronta_render.py --stav        # co chybi
python3 src/promo/pribehy/fronta_render.py --nasucho     # jake prikazy pobezi
python3 src/promo/pribehy/fronta_render.py               # ostry beh
```

Fronta jede **po postech, ne po fazich** — kdyz se preusi v pulce, mas hotove posty,
ne sto karuselu bez jedineho reelu. Stav se cte z disku, takze po padu staci pustit
znovu: dojede jen to, co chybi.

- `--limit N` — jen N postu v tomhle behu (na noc / na test)
- `--jen <slug>` — jen konkretni post, lze vicekrat
- `--znovu` — pregenerovat i hotove
- log: `promo/pribehy/03-posts/fronta.log`

Posty se slozkou `posted-<slug>` (uz publikovane) fronta preskakuje uplne, i pri
`--znovu` — `render_pribeh.py` do nich neumi psat a zalozil by vedle nich duplikat.

Beh je dlouhy (~25 min na post). Poust ho na pozadi a nekontroluj ho v cyklu.

---

# Jednotlivy post (rychla cesta)

Kdyz uzivatel zada jedno tema mimo davku, plati stejne poradi, jen bez fronty.

## Vstupy

- myslenka: `promo/pribehy/01-myslenka/<id>-<slug>.md`
- hotove zneni: `promo/pribehy/02-zneni/<id>-<slug>.md`
- volne historicke tema od uzivatele (vzdy se zdroji)

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
  odmitne): `silueta`, `artefakt`, `osa`, `zakaz`, `krivka`, `typo`. Screen 7 musi
  byt `typo`.
- **`Zvýraznit:`** — presna slova pro rezavy highlight. Musi byt **doslova** v
  headlinu, jinak se highlight nechyti.
- U motivu `silueta` **`Předloha:`** (URL volne dobove fotky), **`Licence:`**,
  **`Výřez:`** a **`Scéna:`** — fotka slouzi jen jako layout reference, vystup je
  vzdy prekreslena ilustrace. Predlohy ber z `katalog_predloh.py --find`. Motiv
  `artefakt` predlohu mit muze, ale nemusi — jeden predmet z promptu vyjde.
- **`## Fakta`** — povinny blok (tvrzeni + zdroj). Vsechny letopocty a cisla z
  headlinu tady musi byt, jinak `render_pribeh.py` generovani odmitne.
- **`## Popisek`** + hashtagy.

### Autorska prava

Pouzit se smi jen snimek volny **i v EU**: `CC0`, `PD-anon-70-EU`, `PD-old-70`,
`PD-old-100`, `PD-France`. Kontrola je vynucena skriptem.

Dve pasti, na ktere skript nestaci, kdyz sahnes mimo katalog:

- `PD-US-no-notice`, `PD-1996` a `PD-US-expired` plati **jen v USA**. V EU se doba
  ochrany pocita od smrti autora — takovy snimek je tady chraneny.
- Stitek **„Public domain" sam o sobe nic nedokazuje**. Rozhoduje az licencni
  kategorie souboru, ne popisek u licence.

## Render pipeline

Prikazy spoustej z korene projektu (`AI-trener`). Skripty pouzivaji `python3`.

### 1. Nacist kontext

- `promo/pribehy/00-nastaveni/pribeh-ramec.md`
- `promo/pribehy/00-nastaveni/styl-pribeh.md`
- vstupni `01-myslenka` / `02-zneni`
- pri renderu i `src/promo/pribehy/render_pribeh.py`, kdyz si nejsi jisty argumenty

### 2. Pripravit zneni

Vytvor / uprav `02-zneni/<id>-<slug>.md` podle ramce. Predlohy dohledej pres
`katalog_predloh.py --find`. Nezapomen na `Story titulek:` a `## Fakta`.

### 3. Kontrola a dry-run

```bash
python3 src/promo/pribehy/zkontroluj_zneni.py --jen <id>-<slug>
python3 src/promo/pribehy/render_pribeh.py --zneni <id>-<slug> --dry-run
```

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

Vystup `reel-kinetic-archiv.mp4` (`1080x1920`, max 25 s, tichy — trending audio se
pridava az v IG appce). Bez `--bpm` casuje skript delku kazdeho slidu podle **poctu
znaku** cteneho textu ve zneni (v cestine lepsi proxy cteni nez pocet slov). `--bpm`
nezadavej — pribehove reely nesnapujeme na beat. Kdyz by reel presahl 25 s, skript
slidy proporcionalne zkrati a rekne o tom.

### 7. Story (jedna title-card)

```bash
python3 src/promo/pribehy/render_story_pribeh.py --post NNN-<slug>
```

Vygeneruje jednu `story.png` (`1080x1920`) **primo v rootu postu**. Titulek bere
z radku `Story titulek:` ve zneni (fallback H1). Prepis lze pres `--title "..."`,
poznamku nad odkaz pres `--note "..."` (vychozi "Celý příběh čtěte tady").
Spodni tretina zustava volna — odkazovy sticker vklada uzivatel rucne v IG appce.

## Kontrola

Mechanicke veci uz overil `zkontroluj_zneni.py`. Rucne se kontroluje jen to, co
skript nevidi:

- **carousel:** 7 finalnich PNG v rootu post slozky, rozmer `1080x1350`, retro paleta
  (ne sportovni), zadny avatar ani logo,
- **reel:** existuje `reel-kinetic-archiv.mp4`, format `1080x1920`, tichy, do 25 s,
- **story:** jedna `story.png` v rootu postu, rozmer `1080x1920`, titulek rekne o CEM
  pribeh je (tema + pointa), spodni tretina volna na sticker,
- **ceska diakritika v obrazku neni rozbita** — over vizualne, model ji obcas spolkne,
- vizualni kontrolu **nedelej sam** (zadny Playwright, zadne screenshoty). Naserviruj
  slozku na localhostu (mimo porty 8080–8089) a posli uzivateli klikaci odkaz:

```bash
cd promo/pribehy/03-posts && python3 -m http.server 5181
```

## Report

Na konci rekni:

- ktera zneni vznikla / byla upravena (a jestli doplnen `Story titulek:`),
- co rekla kontrola (`zkontroluj_zneni.py`) — chyby i varovani,
- jake soubory vznikly (carousel `01-07`, `reel-kinetic-archiv.mp4`, `story.png`)
  a kam,
- co se z reserse do zneni **nedostalo a proc** (blok `## Poznámka k rešerši`),
- odkaz na localhost, kde jde vysledek videt,
- pokud neco neproslo, navrhni jednu cilenou dalsi iteraci.
