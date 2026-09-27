---
name: ubytovani-instance-simple
description: Vygeneruje demo web ubytování ve variantě `simple` ze šablony `sablony/ubytovani-v3/simple` a nasadí ho na Railway jako `{slug}-simple`. Bere URL preview-v2 stránky (`http://127.0.0.1:8000/preview-v2/{slug}`), vytáhne z ní `window.__LEAD__` JSON (název, kontakt, ceník, fotky), vyplní jím `src/content.ts`, zpracuje fotky, otestuje rezervace a nasadí. Použij když uživatel říká "udělej demo z této URL", "vygeneruj instanci z preview-v2", "udělej simple verzi pro [slug]", "nasaď [název chalupy] do šablony". Pro variantu design je samostatný skill `ubytovani-instance-design`.
---

# Demo web ubytování — varianta simple

Z URL preview-v2 vyrobí **demo** web v `~/Můj disk/web-redesign/dema/{slug}/simple/` a nasadí ho na Railway.
Šablona má veškerý obsah v jediném souboru `src/content.ts` — vzhled (`src/routes/index.tsx`, `src/styles.css`)
se při rebrandu **nemění**.

Referenční vyplněná instance: `~/Můj disk/web-redesign/klienti/pivnilazneceskyraj/app/src/content.ts`.
Převod dema na ostrý web (git, volume, heslo do adminu, maily, doména) řeší `~/Můj disk/web-redesign/klienti/NOVY-KLIENT.md`, ne tento skill.

## Invokace

- `/ubytovani-instance-simple http://127.0.0.1:8000/preview-v2/chalupa-cerna-cz`
- „udělej demo z `http://127.0.0.1:8000/preview-v2/chalupa-cerna-cz`“
- „… bez deploye“ / „jen vygeneruj“ → přeskoč fázi 6

**Fallback bez URL:** když uživatel pošle jen podklady (název, kontakt, fotky), polož **jeden** souhrnný dotaz na chybějící údaje a JSON sestav ručně.

## Pre-autorizace deploye

Invokace skillu = souhlas s nasazením na Railway (fáze 6). Neptej se před `railway up`. Jen když uživatel výslovně řekne „bez deploye“, fázi 6 vynech.

## Fáze 1 — URL a cesty

1. URL musí odpovídat `^https?://[^/]+/preview-v2/([a-z0-9-]+)/?$`, jinak se zeptej.
2. `LEAD_SLUG` = poslední část URL (např. `chalupa-cerna-cz`).
3. `SLUG` = `LEAD_SLUG` bez `-cz` a bez pomlček (`chalupacerna`) — název složky, Railway projektu i `site.slug`.
4. `TEMPLATE` = `~/Můj disk/web-redesign/sablony/ubytovani-v3/simple/` (read-only zdroj)
5. `DIR` = `~/Můj disk/web-redesign/dema/{SLUG}/simple/`
6. **Kolize:** existuje-li `DIR`, **nikdy ho nemaž ani nepřepisuj** bez souhlasu. Zeptej se: (a) přerušit, (b) přepsat, (c) nová složka `simple-v2`.
   Pozor: dema založená před 27-09-2026 jsou na starém kódu (centrální API, obsah v `index.tsx`) — přepsáním se převedou na novou šablonu.

## Fáze 2 — data leadu

```bash
curl -s "{URL}" -o /tmp/lead-{LEAD_SLUG}.html
```

Když `curl` selže (server neběží / slug neexistuje), **zastav** a oznam to. Rozparsuj `window.__LEAD__=` (JSON není čistě ukončený → `raw_decode`):

```python
import json
html = open('/tmp/lead-{LEAD_SLUG}.html').read()
idx = html.find('window.__LEAD__=')
if idx < 0:
    raise SystemExit("preview-v2 HTML neobsahuje window.__LEAD__")
data, _ = json.JSONDecoder().raw_decode(html[idx + len('window.__LEAD__='):])
json.dump(data, open('/tmp/lead-{LEAD_SLUG}.json', 'w'), ensure_ascii=False, indent=2)
```

## Fáze 3 — kopie šablony

```bash
rsync -a --exclude node_modules --exclude .git --exclude .output --exclude dist \
  --exclude data --exclude .tanstack "{TEMPLATE}" "{DIR}"
cd "{DIR}" && npm install --no-audit --no-fund
```

## Fáze 4 — obsah do `src/content.ts`

Přepiš **jen** `src/content.ts` (a fotky). Každé pole v šabloně má komentář, co znamená.

| JSON leadu | `content.ts` | Poznámka |
|---|---|---|
| — | `site.slug` | `SLUG` — klíč rezervací v DB |
| — | `site.url` | `https://{SLUG}-simple-production.up.railway.app` — **i v `public/robots.txt` a `public/sitemap.xml`** |
| `brand.name` | `site.name`, `contact.company`, `contact.copyright` | |
| typ objektu | `site.schemaType` | hotel → `"Hotel"`, penzion → `"BedAndBreakfast"`, chalupa/apartmán → `"LodgingBusiness"` |
| typ objektu | `site.icon` | klíč z `IconKey` (`home`, `trees`, `mountain`, `beer`…) |
| `meta.title` / `meta.description` | `site.seo.*` | title ≤ 60, description ≤ 160 znaků |
| `amenities[]` | `site.amenities`, `pricing.included` | jen to, co v leadu je |
| `hero.headline` / `hero.subline` | `hero.titleTop` + `hero.titleMain`, `hero.subtitle`, `hero.features` | `hero.variant`: `"A"` (vlevo s odrážkami, default) nebo `"C"` (etiketa uprostřed) |
| `about.paragraphs[]` | `intro.lines` (2 odstavce), `intro.pillars` (3 karty) | |
| `gallery[]` | `gallery` (8–12 fotek) | první 4 = nejsilnější; mix exteriér / interiér / okolí; hero podle typu (apartmán = interiér) |
| `units[]` | `pricing.room` (+ `pricing.packages` při více typech) | ceny přesně podle leadu |
| `units[]` názvy | `reservation.rooms` | **každý pokoj = vlastní kalendář**; víc pokojů stejného typu = víc položek |
| `surroundings[].places[]` | `surroundings.tips` | `image: null` = ikona místo fotky |
| `contact.*` | `contact.address` (2 řádky: ulice, „PSČ Obec“), `contact.phones`, `contact.email`, `contact.mapQuery`, `contact.facebook` | první telefon = tlačítka „Zavolat“ |
| `faq[]` | `faq` | jen ověřené odpovědi |
| `reviews[]` | `reviews` | jen skutečné |

**Volitelné sekce** — `restaurant`, `pricing.wellness`, `pricing.packages`, `pricing.giftCertificate`, `rating` = `null` → sekce se nezobrazí; `news`, `faq`, `reviews` = `[]` → sekce se nezobrazí. Vyplň je **jen tehdy, když lead obsahuje skutečná data**. Nevymýšlej recenze, hodnocení, restauraci ani wellness.

**Menu** (`nav`) a odkazy v patičce (`contact.footerLinks`) — jen na zapnuté sekce (`#restaurace`, `#akce`, `#faq`… pouze pokud existují).

**Fotky:**
1. Stáhni URL z leadu (`hero.image`, `gallery[].url`, fotky okolí) do `/tmp/`.
2. Převeď do `src/assets/` jako WebP (Pillow): hero max 1920 px, ostatní max 1200 px, `quality=80`, s `ImageOps.exif_transpose`.
3. Importuj je v `content.ts`.
4. Ukázkové fotky šablony (`hero-chalupa.jpg`, `g-*.jpg`, `o-*.jpg`) smaž.
5. Placeholdery (`i.imgur.com` v nízkém rozlišení, `upload.wikimedia.org` stocky místo reálného objektu) uveď v reportu — klient musí dodat skutečné.

## Fáze 5 — kontrola a test

```bash
cd "{DIR}"
grep -rn "Chalupa Pod Lesem\|chalupapodlesem\|example.com" src public   # musí být prázdné
npx tsc --noEmit -p . 2>&1 | grep "src/" | grep -v "__root.tsx"          # musí být prázdné (chyba v __root je známá)
npm run build
# lokální test — volný port mimo 8080–8089, cwd do /tmp, ať DB nevznikne v instanci
(cd /tmp && PORT=8099 node "{DIR}/.output/server/index.mjs" &) ; sleep 4
BASE_URL=http://localhost:8099 node scripts/test-rezervace.mjs            # bez ADMIN_PASSWORD přeskočí testy adminu
```
Server po testu ukonči (jen ten, který jsi spustil).

## Fáze 6 — Railway

Demo **nepotřebuje** volume ani proměnné: admin je bez `ADMIN_PASSWORD` vypnutý, maily bez `RESEND_API_KEY` jen logují, rezervace bez volume jsou dočasné.

```bash
cd "{DIR}"
railway list | grep -x "  {SLUG}-simple"      # existuje už projekt?
```
- **Neexistuje:** `railway init --name {SLUG}-simple`
- **Existuje** (i prázdný, bez služby): `railway link -p {SLUG}-simple -e production`, pak `railway add --service {SLUG}-simple`

Pak:
```bash
railway status            # OVĚŘ, že Project = {SLUG}-simple (složky bývají omylem nalinkované na cizí projekt)
railway service {SLUG}-simple
railway up --ci
railway domain            # https://{SLUG}-simple-production.up.railway.app
curl -s -o /dev/null -w "%{http_code}\n" -L https://{SLUG}-simple-production.up.railway.app/   # 200
BASE_URL=https://{SLUG}-simple-production.up.railway.app node scripts/test-rezervace.mjs
```

Když build na Railway selže: `railway logs --deployment` ukazuje **aktivní** deploy, ne ten spadlý — skutečnou chybu dohledej podle skillu `lovable-railway-deploy` (sekce „Diagnostika FAILED deploye“). Nejčastěji nesedí `package-lock.json`.

`railway.json` ze šablony spouští přímo `node` (ne `npm start`) — jinak Railway při každém deployi hlásí falešné „Deployment crashed“.

## Finální report

- Cesta `{DIR}` a URL `https://{SLUG}-simple-production.up.railway.app`
- Co se z leadu vyplnilo (sekce, počet fotek, pokoje) a které volitelné sekce jsou zapnuté
- Co chybí / je placeholder → musí dodat klient
- Výsledek testu rezervací (lokálně i na Railway)

Na konec **vždy** nabídkový e-mail k odeslání (plain text v code blocku, bez markdown odrážek, s reálnou URL):

```
Dobrý den,

cena za kompletně nový web včetně rezervačního systému je:

4 900 Kč jednorázově — tvorba a nasazení webu, rezervační systém
490 Kč měsíčně — správa webu:

Hosting a zabezpečení webu
Zálohování a aktualizace
Drobné obsahové úpravy
Technická podpora při problémech
Přehled návštěvnosti a výkonu webu

Vaše doména zůstává u stávajícího registrátora — jen u něj v administraci vložíte jeden DNS záznam, který přesměruje doménu na můj hosting. Poradím vám přesně, kam kliknout, trvá to 5 minut.

Pro představu jsem připravil návrh nového webu: https://{SLUG}-simple-production.up.railway.app

S pozdravem,
Lukáš Vozdecký
buildai.cz
```

## Anti-patterns

- **Nesahej na šablonu** `sablony/ubytovani-v3/simple` — je to read-only zdroj. Chyba v šabloně = oprav ji zvlášť a pak přegeneruj demo.
- **Neupravuj `index.tsx` ani `styles.css`** při rebrandu — jen `content.ts` a fotky. Chybí-li sekce, kterou klient potřebuje, zeptej se (patří do šablony pro všechny).
- **Nevymýšlej obsah** — recenze, hodnocení, restauraci, wellness, vybavení. Prázdná sekce se skryje sama.
- **Nepoužívej centrální API** `ubytovani-api` — neexistuje; `simple` má rezervace v aplikaci.
- **Nepřepisuj existující demo** bez souhlasu (fáze 1).
- **Neměň porty 8080–8089** — rezervované pro mail-agenty.
