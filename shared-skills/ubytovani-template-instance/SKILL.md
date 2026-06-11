---
name: ubytovani-template-instance
description: Vygeneruje novou klientskou instanci z template `web-redesign-ubytovani-template-v3` (TanStack Start + React). Bere jako parametr URL preview-v2 stránky (`http://127.0.0.1:8000/preview-v2/{slug}`), z níž vytáhne `window.__LEAD__` JSON s názvy, kontaktem, ceníkem, fotkami. Naklonuje template do nové složky `web-redesign-{slug}/` a kompletně ho rebrandne. Ruční vstupy slouží jen jako fallback pro chybějící pole. Použij když uživatel říká "udělej v3 z této URL", "vygeneruj instanci z preview-v2", "nasaď [název chalupy] do template v3".
---

# Ubytování template — generátor klientské instance

Skill, který z URL preview-v2 stránky vygeneruje **novou** klientskou instanci template `web-redesign-ubytovani-template-v3`. Naklonuje template do nové složky pojmenované podle slugu a kompletně přepíše branding (texty, fotky, kontakt, ceník) podle dat z `window.__LEAD__` JSONu. Všechny texty jsou roztroušené po jednom souboru (`src/routes/index.tsx`) + složce `src/assets/`.

## Invokace

**Primární vstup = URL parametr.** Uživatel typicky řekne jednu z variant:

- `/ubytovani-template-instance http://127.0.0.1:8000/preview-v2/chalupa-cerna-cz`
- "udělej v3 z `http://127.0.0.1:8000/preview-v2/chalupa-cerna-cz`"
- "vygeneruj instanci z této URL: ..."

URL musí mít formát `http(s)://{host}:{port}/preview-v2/{slug}`. Slug z URL slouží jak k pojmenování nové složky, tak jako `VITE_LEAD_SLUG` v `lead-data.ts`.

**Sekundární vstup (fallback):** Pokud uživatel nepošle URL, ale jen klientské podklady (název, kontakt, fotky), použij ruční dotazy (viz dále) a vygeneruj instanci stejným postupem, jen JSON sestav ručně.

## Kdy použít

- Uživatel pošle URL preview-v2 — to je hlavní use-case. Vygeneruješ z ní novou instanci v sourozenecké složce.
- Uživatel říká "udělej v3 z preview-v2", "vygeneruj instanci pro [slug]", "připrav klientskou kopii template".
- **Nepoužívej** pro:
  - Drobné textové opravy v existující instanci — udělej přímou editací.
  - Modifikaci samotného template (`-template-v3` repozitáře) — to není instance, to je zdroj.

## Co skill nemění

- Designový systém (barvy `walnut/forest/sepia/ivory/parchment`, fonty, layout, fotorámeček, pásky, dekorace `botanical-branch.png` a `mountain-sketch.png`).
- `DeerLogo` v navigaci — pokud klient nedodá vlastní logo, zůstává jelen (template má jelena v jméně i v případě "Zelený Jelen", ale jako generický horský motiv funguje pro většinu chalup; pokud klient nechce jelena, **explicitně se zeptej** a nahraď jiným SVG nebo textovým monogramem).
- Strukturu sekcí (Nav, Hero, Story, Interior, GuestBook, OwnerTips, LocalMap, Footer).
- **Rezervační systém** — `ReservationSection.tsx` z `design/` je referenční. Pokud klonuješ `simple/`, nahraď tamní lokální `ReservationWidget` touto implementací (viz sekce „Rezervační systém — implementace v instanci" níže). Logika (flatpickr, hotelová konvence blokování, kolize check) a popisky se nemění.

## Workflow — vytvoření nové instance z URL

Tohle je **hlavní postup**. Skill běží v cestě, kde existuje sourozenecký template (typicky `~/Můj disk/web-redesign/` nebo `~/claude-code/`). Postup má 4 fáze:

### Fáze 1 — parsing URL a příprava cest

1. **Validuj URL** — musí matchovat regex `^https?://[^/]+/preview-v2/([a-z0-9-]+)/?$`. Pokud ne, zeptej se uživatele.
2. **Extrahuj slug** — poslední část path (např. `chalupa-cerna-cz`).
3. **Odvoď cesty:**
   - `TEMPLATE_DIR` = sourozenecký adresář `web-redesign-ubytovani-template-v3` (pokud uživatel pustí skill z jiné cesty, najdi ho přes `find` nebo se zeptej).
   - `INSTANCE_DIR` = `{parent_of_template}/web-redesign-{slug_bez_-cz}/`. Konvence: slug `chalupa-cerna-cz` → složka `web-redesign-chalupacerna` (odstranit `-cz` suffix a všechny pomlčky). Pokud uživatel preferuje jinou konvenci nebo už složku má, zeptej se.
4. **Kolize?** Pokud `INSTANCE_DIR` existuje, **NIKDY ho automaticky nemaž ani nepřepiš**. Zeptej se uživatele:
   - "Adresář `{INSTANCE_DIR}` existuje. Mám (a) přerušit, (b) přepsat (ztratíš změny), (c) přidat suffix `-v2`?"

### Fáze 2 — extrakce lead JSON

```bash
curl -s "{URL}" -o /tmp/lead-{slug}.html
```

Pokud `curl` selže (ECONNREFUSED, 4xx, 5xx): server neběží nebo slug neexistuje. **Nezačínej klonovat** — zastav a oznam chybu uživateli.

Rozparsuj `window.__LEAD__=` (JSON není čistě ukončený, použij `raw_decode`):

```python
import json
html = open('/tmp/lead-{slug}.html').read()
idx = html.find('window.__LEAD__=')
if idx < 0:
    raise SystemExit("preview-v2 HTML neobsahuje window.__LEAD__")
start = idx + len('window.__LEAD__=')
data, _ = json.JSONDecoder().raw_decode(html[start:])
json.dump(data, open('/tmp/lead-{slug}.json', 'w'), ensure_ascii=False, indent=2)
print(json.dumps(data, ensure_ascii=False, indent=2))
```

Ulož JSON i do `/tmp/lead-{slug}.json` pro pozdější referenci.

### Fáze 3 — klonování template

**Preferovaná metoda — čistá kopie bez node_modules / .git:**

```bash
rsync -a \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='.output' \
  --exclude='dist' \
  --exclude='.vite' \
  --exclude='bun.lock' \
  "{TEMPLATE_DIR}/" "{INSTANCE_DIR}/"
```

Pak v instanci:

```bash
cd "{INSTANCE_DIR}"
git init -q
npm install   # nebo bun install — ať použije stejný PM jako template (zkontroluj přítomnost bun.lock / package-lock.json)
```

**Alternativa** (pokud template je git repo se shared historií): `git clone {TEMPLATE_DIR} {INSTANCE_DIR}` + `rm -rf .git && git init`. Nepoužívej pokud template není v gitu.

### Fáze 4 — rebrand instance

Pokračuj editací souborů v `{INSTANCE_DIR}` podle sekcí níže ("Mapování JSON → template" + "Workflow — kroky v kódu"). **Nikdy nemodifikuj `{TEMPLATE_DIR}` během tohoto skillu** — template je read-only zdroj.

Na konec spusť kontrolu (Grep zbylých referencí + build) v `{INSTANCE_DIR}`, ne v template.

---

## Vstupy — mapování dat z preview-v2

Pokud uživatel poskytl URL ve formátu `http(s)://{host}/preview-v2/{slug}`, lead JSON se vytáhne podle Fáze 2 výše. Z něj se rebrand téměř kompletně sestaví automaticky bez dotazování uživatele.

### Mapování JSON → template

Lead JSON má tato pole — namapuj je na sekce v `src/routes/index.tsx`:

| JSON cesta | Cíl v template | Poznámka |
|---|---|---|
| `slug` | `src/lib/lead-data.ts` → default `VITE_LEAD_SLUG` | použij pro Reservation API |
| `meta.title` | `<title>` + `og:title` (řádky ~24, 30) | ořež na ≤60 znaků |
| `meta.description` | `description` + `og:description` (řádky ~27, 32) | ≤160 znaků |
| `brand.name` | Logo v Nav (řádek ~75–76), citáty, footer copyright | rozsekni na 2 spans pokud je víceslovný |
| `brand.location` | Pod logem `— ČESKÉ HORY —` (řádek ~77), Footer adresa | velkými písmeny v logu |
| `hero.headline` | H1 v Hero (řádek ~114–119) | obal klíčové slovo `<em className="italic text-forest">` |
| `hero.subline` | Popisek pod H1 (řádek ~121–124) | |
| `hero.image` | **stáhni** a ulož jako `src/assets/hero-pension.webp` (případně konvertuj) | |
| `about.headline` | Story H2 nadpis (řádek ~187–189) | |
| `about.paragraphs[]` | 3 odstavce dopisu ve Story (řádky ~244–259) | pokud je < 3, doplň generickými větami |
| `about.image` | nahraď `current-pension.jpg` | |
| `about.owner_name` | Příjmení → "rodina XY ♡" podpisy; křestní jméno → OwnerTips nadpis | rozparsuj na křestní + příjmení |
| `about.owner_image` | nahraď `owner-illustration.png` (pokud je to ilustrace) nebo ponech default | |
| `units[]` | Pricing sekce (řádky ~813–833) | každá `unit` = jedna karta; namapuj `name`, `capacity`, `meta`, `features`, `price` |
| `amenities[]` | volitelné — můžeš zkombinovat s ValuesStrip nebo přidat jako podsekci v Interior | nepřebij designové ikony zbytečně |
| `gallery[]` | Interior sekce — vezmi prvních 4 fotek a ulož jako `interior-living.webp`, `interior-kitchen-dining.webp`, `interior-bedroom.webp`, `interior-kitchen.webp` | pokud gallery má < 4, použij stejnou fotku víckrát nebo `hero.image` |
| `surroundings[].places[]` | OwnerTips `tips` array (řádky ~530–549) | mapuj `name` → `title`, `description` → `desc`, `distance` → `time`; ikony přiřaď tematicky |
| `surroundings[]` jako popis | LocalMap popisek (řádky ~624–628) | sestav 2-3 věty z názvů míst |
| `contact.address` | Footer "Kde nás najdete" (řádky ~687–694) | rozsekni na 3 řádky |
| `contact.phone_display` (nebo `phone`) | Footer "Spojení" (řádky ~698–700) | pokud prázdné, vynech řádek |
| `contact.email` | Footer "Spojení" (řádek ~701) | |
| `contact.maps_embed_url` | `<iframe src="...">` ve Footer mapě (řádky ~713) | |
| `cta.headline`, `cta.subline` | volitelně do Footer claim nebo ReservationSection | |
| `faq[]` | template nemá FAQ sekci — **ignoruj** nebo se zeptej zda přidat |
| `reviews[]` | pokud má >0 položek, použij v GuestBook místo template recenzí | pokud prázdné, ponech template fallback |

### Co preview-v2 NEMÁ a musíš se zeptat nebo nechat default

- **Hero citát** (rukopis u portrétu rodiny) — preview-v2 to nemá. Nech template default nebo nahraď generickou variantou z `about.paragraphs[0]`.
- **Story diptych "dříve/dnes"** — preview-v2 obvykle nemá historickou fotku. **Smaž `<figure>` s `historicImg`** a uprav grid (viz sekce Workflow níže).
- **GuestBook vzkazy** — pokud `reviews[]` je prázdné, **ponech template texty** (klient může později přidat). Negeneruj falešné recenze.
- **ValuesStrip** (4 ikony pod Story) — zachovej default texty nebo zkombinuj s `trust_items[]` z JSON.

## Vstupy — fallback: ruční dotazy

Použij **pouze když**:
- Preview-v2 URL není dostupná / server neběží / slug neexistuje.
- Konkrétní pole v JSON je prázdné a nelze ho rozumně vyvodit z ostatních.

Polož **jeden souhrnný dotaz** (ne 10 zpráv po jednom). Použij `AskUserQuestion` s následujícími položkami nebo nech uživatele odpovědět volnou formou:

1. **Název objektu** — celý + zkrácený (např. "Apartmány Zelený Jelen" / "Zelený Jelen"). Použije se v navu, meta tagech, footeru, citátech.
2. **Region/lokalita** — co stojí pod logem (např. "České hory", "Šumava", "Jeseníky") a v adrese.
3. **Příjmení rodiny / majitele** — pro podpisy ("rodina XY ♡", "rodina XY zdraví").
4. **Křestní jméno majitele** — pro sekci OwnerTips ("Pavlovy oblíbené zákoutí" → "[Jméno]ovy oblíbené zákoutí").
5. **Hero citát** (2 řádky + podpis) — krátký osobní vzkaz v Hero sekci. Pokud klient nedodal, použij šablonu a uprav podle ladění objektu.
6. **Story** — krátký příběh objektu (3 odstavce do dopisu v sekci Story). Pokud klient nedodal, vytvoř návrh ze 3 vět a nech uživatele schválit.
7. **Tipy majitele** — 3 doporučení v okolí (název, popis 1 věta, vzdálenost/čas). Default jsou kavárna, lesní stezka, vyhlídka — necháme stejnou strukturu, jen přepíšeme obsah podle reálných míst.
8. **Lokální názvy pro Mapu okolí** — kopce/potoky/vesnice okolo (jeden odstavec, text pod nadpisem "Mapa okolí").
9. **Kontakt** — adresa (3 řádky), telefon, email, otevírací doba.
10. **Meta** — title (≤60 znaků), description (≤160 znaků), OG title/description.

## Vstupy — assets

**Primární zdroj fotek = URL v lead JSON** (`hero.image`, `about.image`, `about.owner_image`, `gallery[].url`). Stáhni je přes `curl -o src/assets/{cilovy_nazev}.{ext}` a v případě potřeby konvertuj formát (viz níže).

**Fallback = fotky od klienta** v lokální složce (typicky `~/Downloads/klient-XY/`) — použij když lead JSON odkazuje na placeholder obrázky (imgur generické nebo wikimedia stocky), nebo klient pošle vyšší kvalitu.

Cílové názvy v `src/assets/` (zachovej je — odkazují se z kódu):

| Soubor | Účel | Co dělat když chybí |
|---|---|---|
| `hero-pension.webp` | Hlavní hero fotka (exteriér, navečer / "atmosférická") | povinné — bez ní instance nevypadá |
| `current-pension.jpg` | "Dnes" — současný pohled na objekt | použij druhou exteriérovou fotku |
| `historic-pension.jpg` | Historická černobílá fotka | pokud nemá, navrhni odstranit celý "dříve/dnes" diptych a Story nechat jen s dopisem + jednou aktuální fotkou |
| `interior-living.webp` | Obývák / společenská místnost | povinné pro Interior sekci |
| `interior-kitchen-dining.webp` | Kuchyň + jídelna | povinné |
| `interior-bedroom.webp` | Ložnice | povinné |
| `interior-kitchen.webp` | Detail kuchyně | povinné (4. fotka v Interior gridu) |
| `watercolor-map.png` | Ručně kreslená mapa okolí | klíčové — bez ní vypni celou sekci LocalMap nebo nahraď statickým obrázkem |
| `owner-illustration.png` | Ilustrace majitele (kreslená postava) | pokud nemá, lze nahradit kulatou fotkou majitele nebo schovat |
| `botanical-branch.png`, `mountain-sketch.png` | Dekorace (větvička, hory v pozadí) | ponechat — jsou neutrální |

**Workflow s fotkami z lead JSON (primární):**

1. Vezmi `hero.image`, `about.image`, `about.owner_image`, `gallery[].url` z extrahovaného JSON.
2. Stáhni do `/tmp/` přes `curl -sL {url} -o /tmp/hero.{ext}`.
3. Konvertuj/přejmenuj do `src/assets/` pod cílové názvy (viz `sips` níže).
4. **Kontrola placeholders:** pokud URL ukazuje na `i.imgur.com` s nízkým rozlišením nebo na `upload.wikimedia.org` (stock fotka, ne reálný objekt), **upozorni uživatele** — pravděpodobně potřebuje reálné fotky a měl by je dodat ručně. Nepoužívej stocky jako finální assets.

**Workflow s fotkami od klienta (fallback / doplnění):**

1. Uživatel ti dá cestu k dodaným fotkám (typicky `~/Downloads/klient-XY/` nebo Google Drive složka).
2. Pro každou fotku zjisti rozlišení (`sips -g pixelWidth -g pixelHeight FILE` na macOS). Hero a current chtějí ≥1600 px šířky, interiéry ≥1200 px.
3. Zeptej se **která fotka je hero** — výběr je důležitý, jde o úvodní dojem. Pokud uživatel váhá, navrhni kandidáty (exteriér + atmosférické světlo).
4. Zkopíruj/přejmenuj do `src/assets/` pod cílové názvy z tabulky výše. Vstupní formát respektuj — `.webp` necháváš `.webp`, `.jpg` necháš `.jpg`. Pokud klient pošle `.HEIC` nebo `.png` na pozici `.webp`, převed přes `sips`:
   ```
   sips -s format jpeg vstup.HEIC --out src/assets/current-pension.jpg
   sips -s format png vstup.HEIC --out src/assets/watercolor-map.png
   ```
5. **Komprese:** hero ideálně ≤300 KB, interiéry ≤200 KB. Pokud jsou větší, použij `cwebp -q 80` nebo `sips -s formatOptions 75`.

## Workflow — kroky v kódu

Pracuješ v naklonované **instanci** (`{INSTANCE_DIR}`), ne v template. Editace probíhá ve dvou souborech:
- `{INSTANCE_DIR}/src/lib/lead-data.ts` — nastav default `slug` na `{slug}` z URL (řádek `?? "..."`)
- `{INSTANCE_DIR}/src/routes/index.tsx` — všechen branding (níže)

Všechna místa k úpravě v `index.tsx`:

### 1. Meta tagy (řádky ~17–29)
- `title` v `meta` array — celý název + krátký claim
- `name="description"` — 1 věta
- `og:title`, `og:description`, `og:image` (image zůstává `heroImg` — nahradíš jen soubor)

### 2. Nav — logo + region (řádky ~62–70)
- `<span>APARTMÁNY</span>` + `<span>ZELENÝ JELEN</span>` — rozděleno na 2 řádky velkými písmeny
- `— ČESKÉ HORY —` pod logem
- Pokud má klient jednoslovný název ("Chalupa Lipka"), použij jen jeden span: `<span>CHALUPA</span><span>LIPKA</span>` nebo sluč do jednoho s `tracking-[0.18em]`.

### 3. Hero (řádky ~92–158)
- Úvodní prskaný text `— vítejte u nás —` — necháváš nebo přizpůsobíš (např. `— vítejte na chalupě —`).
- H1: `Místo, kde se čas zastoupí na chvíli.` — pokud klient chce vlastní claim, přepiš. **Zachovej `<em className="italic text-forest">…</em>`** kolem klíčového slova.
- Popisek pod H1 (~3 věty) — přepsat podle objektu.
- Citát na konci levého sloupce + podpis `— rodina Žďárských`.
- Alt hero fotky — popis objektu (povinné pro SEO).
- Hand-text pod fotkou: `vítá vás Zelený Jelen ✦` → `vítá vás [Název] ✦`.

### 4. Story (řádky ~162–263)
- Nadpis: `Jak se ze srubu stal <em>Zelený Jelen</em>` — přepiš na příběh objektu. Zachovej `<em>` pro slovo, které je zelené (typicky název).
- Podtitul (~2 řádky kurzívou).
- 3 odstavce dopisu — přepiš celé.
- Podpis `rodina Žďárských ♡` → `rodina [Příjmení] ♡`.
- Pokud klient nedodal historickou fotku, **smaž celý prvek `<figure>` s `historicImg`** a uprav grid z `lg:grid-cols-[1fr_1fr_1.1fr]` na `lg:grid-cols-[1fr_1.2fr]`.
- ValuesStrip (4 ikony) — texty `Rodinný podnik / Osobní přístup / Láska k horám / Poctivá snídaně` přizpůsob jen pokud klient výslovně chce. Defaultně necháváš.

### 5. Interior (řádky ~287–381)
- Pole `photos` má 4 položky — uprav `alt` a `caption` podle reálných pokojů. `caption` jsou krátké ručně-psané popisky (max 3 slova + emoji).
- Nadpis `Pohled dovnitř` většinou necháváš.
- Popisek pod nadpisem (3 věty) — přizpůsob materiálu/atmosféře objektu.

### 6. GuestBook (řádky ~383–516)
- 5 vzkazů + 1 dětská kresba. Pokud klient dodal **reálné recenze**, použij je. Pokud ne, **necháváš template texty** — zákazníky to nemate, působí to "obydleně" (klient může později doplnit).
- Pokud klient výslovně chce čisté pole připravené pro vlastní vzkazy, zredukuj na 2 generické vzkazy s neutrálními jmény ("Marie & Tomáš, červen").

### 7. OwnerTips (řádky ~518–604)
- Nadpis `Pavlovy oblíbené zákoutí` → `[Jméno majitele]ovy oblíbené zákoutí`. Pozor na české skloňování — pokud jméno končí na souhlásku, použij `-ovy` (Pavl**ovy**, Petr**ovy**), na samohlásku jinak (`Lukáš` → `Lukášovy`, `Honza` → `Honz**ovy**`). Pokud nejde, použij neutrální `Tipy od pana domácího`.
- 3 tipy v poli `tips` — přepsat název, popis, čas. Ikony (`CupIcon`, `LeafIcon`, `MountainIcon`) přiřaď tematicky.
- Citát v bublině: `Když u nás budete, určitě zajděte aspoň na jedno z těchto míst.` — můžeš nechat.
- Alt ilustrace majitele: `Ilustrace pana [Jméno], majitele [objektu]`.

### 8. LocalMap (řádky ~606–642)
- Nadpis `Mapa okolí` — necháváš.
- Popisek (3 věty) s názvy okolních kopců/potoků/vesnic — **klient musí dodat**, jinak se zeptej.
- Alt mapy: `Ručně malovaná mapa okolí [Název]`.

### 9. Footer (řádky ~644–715)
- H2 claim `Těšíme se, až vás přivítáme u nás.` — necháváš.
- Adresa (3 řádky), telefon, email, otevírací doba — z kontaktu klienta.
- Podpis `S láskou, rodina Žďárských ♡` → `S láskou, rodina [Příjmení] ♡`.
- Copyright dole: `APARTMÁNY ZELENÝ JELEN` → název klienta velkými písmeny.

## Kontrola na konec

Vše spouštěj v `{INSTANCE_DIR}`, ne v template.

1. **Grep zbylé reference** — `Grep "Zelený Jelen|Žďárských|České hory|Pavl|Stachy|Suchý Vrch|Stašský|Kovářův|Horní Lipka|zelenyjelen" {INSTANCE_DIR}/src`. Mělo by být 0 výsledků (kromě možného `DeerLogo` SVG komentáře).
2. **Build** — `npm run build` (nebo `bun run build`, podle PM) musí projít bez warningů o chybějících assets.
3. **Dev server** — `npm run dev` + screenshot všech sekcí přes Playwright MCP. Vizuálně zkontroluj:
   - Hero fotka nemá divný ořez (`object-cover` může něco useknout)
   - Ručně kreslená mapa není rozmazaná
   - Texty se nikde nelámou divně (claim v Hero, OwnerTips nadpis)
4. **Lighthouse** — pokud klient bude deployovat, spusť `npm run build && npx serve -s dist` + Lighthouse. Mobilní skóre by mělo být ≥85.
5. **Reportuj uživateli:**
   - Cestu k nové instanci (`{INSTANCE_DIR}`)
   - Co všechno bylo vytaženo z lead JSON
   - **Co chybí** (placeholder fotky, prázdná pole jako telefon, prázdné `reviews[]`) — to musí klient ještě dodat
   - Příkaz pro spuštění dev serveru a URL kde běží

## Cesty (cross-platform)

- **Template root** (read-only zdroj): repo `web-redesign-ubytovani-template-v3/` má **dvě varianty** v podsložkách:
  - `web-redesign-ubytovani-template-v3/design/` — bohatá "paper-card" varianta (walnut/forest/sepia paleta, flatpickr, kompletní rezervační systém s API proxy).
  - `web-redesign-ubytovani-template-v3/simple/` — minimalistická bootstrap-like varianta (foreground/primary/muted tokeny, lokální react-day-picker + SQLite widget jako placeholder).
- Pokud uživatel neupřesní, **zeptej se** kterou variantu chce klonovat. Default = `design` pro plnou implementaci, `simple` pro rychlý prototyp.
- **Instance root** (cíl skillu): `{parent_of_repo}/web-redesign-{slug_simplified}/`.
- **Assets**: `src/assets/` (relativní vůči instance root).
- **Hlavní soubor**: `src/routes/index.tsx`.

Nikdy nepoužívej absolutní cesty s `/Users/lukas/` v kódu, jen v Bash příkazech.

## Rezervační systém — implementace v instanci

Cílový rezervační systém je referenčně implementovaný v `design/` variantě. Pokud klient klonuje z `simple/`, lokální widget je jen placeholder — **nahraď ho stejnou implementací jako v `design/`**, aby instance volala produkční FastAPI backend.

### Architektura

- **Backend**: FastAPI rezervační API, lokálně na `http://127.0.0.1:8000`, produkce na `https://ubytovani-api-production.up.railway.app` (nebo aktuální Railway URL, ověř s uživatelem).
- **Endpointy**: `GET /api/rezervace/{slug}` (list), `POST /api/rezervace/{slug}` (vytvoř), `PATCH /api/rezervace/{slug}/{id}/zrusit` (zruš).
- **Slug**: identifikuje instanci v API; drží se v `src/lib/lead-data.ts`, default přebije `VITE_LEAD_SLUG` env. Konvence slug = `{slug-z-preview-v2}` (např. `penzionorlicko-cz`, **včetně** `-cz` suffixu — to je primární klíč v API DB).
- **Komponenta**: `src/components/ReservationSection.tsx` — flatpickr s českou lokalizací, dvě date inputy (příjezd/odjezd), distinct seznam pokojů z existujících rezervací, hotelová konvence blokování dnů (X je blokovaný iff je obsazený přes noc i ráno současně), kolize check, tabulka přehledu rezervací s tlačítkem Zrušit.
- **Proxy**:
  - **Dev** (vite): `vite.config.ts` → `vite.server.proxy["/api"]` → `http://127.0.0.1:8000`.
  - **Prod** (nitro/Railway): `vite.config.ts` → `nitro.routeRules["/api/**"]` → `https://ubytovani-api-production.up.railway.app/api/**`. Bez tohohle by Nitro v SSR nevěděl kam `/api` zařídit.

### Pokud klonuješ z `simple/` — postup integrace

`simple/` má jiný widget (`ReservationWidget.tsx`) + lokální SQLite (`reservations.ts`, `reservations-db.ts`). Plná náhrada za referenční systém:

1. **Smaž lokální systém v instanci** (v instanci, ne v template):
   ```bash
   rm src/components/ReservationWidget.tsx src/lib/reservations.ts src/lib/reservations-db.ts
   ```
2. **Přidej deps**:
   ```bash
   npm install flatpickr
   ```
   (`better-sqlite3` může v `package.json` zůstat — nevadí. Jen ho instance nepoužívá.)
3. **Vytvoř `src/lib/lead-data.ts`** se slug klienta (z preview-v2 URL, **včetně `-cz` suffixu**):
   ```ts
   export const leadData = {
     slug: (import.meta.env.VITE_LEAD_SLUG as string | undefined) ?? "{slug-z-url}",
   };
   ```
4. **Vytvoř `src/components/ReservationSection.tsx`** — zkopíruj jako vzor `web-redesign-ubytovani-template-v3/design/src/components/ReservationSection.tsx`. Vizuálně přizpůsob paletě cílové instance:
   - Pokud instance vychází z `simple/`, použij utility tokeny `foreground/primary/muted/card/border/input` místo `walnut/forest/sepia/ivory/parchment/paper-card/tape/font-hand/font-display`.
   - Validační hlášky, info panel pro majitele, popisky labels (Datum příjezdu/odjezdu, Pokoj, Jméno a příjmení, Telefon, E-mail) **zachovej beze změny** — jsou součástí UX.
5. **Uprav `vite.config.ts`** — přidej dev proxy a prod nitro routeRules:
   ```ts
   nitro: {
     preset: "node-server",
     routeRules: {
       "/api/**": {
         proxy: "https://ubytovani-api-production.up.railway.app/api/**",
       },
     },
   },
   vite: {
     server: {
       proxy: {
         "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
       },
     },
   },
   ```
6. **Nahraď v `src/routes/index.tsx`**:
   - Import: `import { ReservationSection } from "@/components/ReservationSection";`
   - Sekce: nahraď `<ReservationWidget showAdmin />` za `<ReservationSection />`, přidej header s textem **"napište nám termín" → "Zarezervujte si pobyt"** + krátký popisek "Vyberte si termín v kalendáři a vyplňte krátkou poptávku. Termín se okamžitě zablokuje pro ostatní hosty."

### Ověření

Po integraci:
1. **Backend musí běžet** na :8000, jinak fetch selže s ECONNREFUSED. Pokud neběží, upozorni uživatele — neimplementuj fallback.
2. `curl http://localhost:{port}/api/rezervace/{slug}` → HTTP 200 + JSON array (proxy funguje).
3. Načtení homepage zobrazí dvě karty: formulář + tabulku rezervací s existujícími záznamy z DB.
4. Vyber termín v kalendáři → flatpickr disabluje plně obsazené dny (noc & ráno).

## Anti-patterns

- **Nikdy nemodifikuj `web-redesign-ubytovani-template-v3/`** — to je read-only zdroj. Všechen rebrand jde do nově naklonované `web-redesign-{slug}/` instance.
- **Nepřepiš existující instanci** bez explicitního souhlasu uživatele (viz Fáze 1, kolize cest).
- **Nedělej** "drobné vylepšení" struktury (sekce navíc, nové komponenty, refaktor) — klient platí za rebrand, ne za přestavbu. Pokud něco potřebuje strukturální změnu, zeptej se.
- **Neměň** designové tokeny v `src/styles.css` bez explicitního souhlasu — barevný systém je vyladěný.
- **Negeneruj** fotky AI obrázkovým modelem, pokud klient neřekne výslovně. Reálné fotky objektu jsou jediný zdroj autenticity.
- **Nepřekládej** sekce do angličtiny. Template je čistě česky, klienti jsou české ubytko.
- **Nedělej lokální DB v instanci** (better-sqlite3 / lokální SQLite tabulka rezervací). Rezervace patří do centrálního FastAPI backendu — instance jen volá `/api/rezervace/{slug}` přes vite/nitro proxy. Pokud `simple/` template má lokální SQLite widget, je to placeholder a má se nahradit (viz výše).
- **Neměň slug formát** mezi preview-v2 a `lead-data.ts`. Pokud preview-v2 URL končí `-cz`, slug v `lead-data.ts` musí mít `-cz` taky — backend DB to čeká.
