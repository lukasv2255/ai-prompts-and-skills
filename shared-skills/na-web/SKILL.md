---
name: na-web
description: >
  Vystaví hotový HTML dokument z projektového adresáře na web buildai.cz. Zkopíruje
  ho do `web/site/hosted/<projekt>.html`, prověří osobní údaje a nabídne anonymizaci,
  commitne, pushne a počká, až je stránka živá.

  Použij kdykoliv uživatel říká:
  - "dej to na web"
  - "commit a push na web"
  - "vystav ten report"
  - "publikuj to na buildai"
  - "/na-web <soubor>"
---

# na-web — vystavení HTML na buildai.cz

Pracovní postup uživatele je vždy stejný: **nejdřív vzniká dokument v adresáři projektu**
(report, nabídka, prezentace), tam se ladí, a teprve hotová verze se vystaví na web.
Tenhle skill dělá jen ten poslední krok.

---

## Kde co žije

| | Cesta | Role |
|---|---|---|
| **Zdroj** | `<projekt>/<cokoliv>.html` | pracovní verze, tady se edituje |
| **Web** | `~/Můj disk/AI-brand/AI-brand-me/web/site/hosted/<projekt>.html` | co je vystavené |
| **Evidence** | `web/site/hosted/README.md` | odkud který soubor je a kdy se překlápěl |
| **Adresa** | `https://www.buildai.cz/<projekt>` | bez přípony `.html` |

Web je **jeden pro všechny projekty**. Nasazuje se z `web/site/` přes Railway
(vlastní `Dockerfile` a `railway.json` v té složce), deploy se spouští pushem na
`main` a naběhne do půl minuty.

**Název souboru určuje adresu.** `web/site/hosted/springwalk.html` je
`buildai.cz/springwalk` — `/hosted` se v adrese neobjeví, nginx ho zkouší jako
poslední možnost (`try_files … @hosted` v `docker/nginx.conf`).
Nepřejmenovávej existující soubor, rozbil by se odkaz, který už někdo má.

**Kořen `web/site/` je web značky, `hosted/` jsou hosté z projektů.** Nové soubory
z projektů patří vždy do `hosted/`. Podrobnosti v `web/site/hosted/README.md`.

**Konfiguraci nginx měň jen v `docker/nginx.conf`.** Produkce se buildí z kořenového
`Dockerfile` (Root Directory `/`); `web/site/Dockerfile` a `web/site/railway.json`
jsou mrtvý zbytek po starém CLI deployi a nic z nich se nenasazuje.

---

## Postup

### 1. Najdi zdroj a cíl

Pokud uživatel soubor nepojmenoval, vezmi ten, na kterém se právě pracovalo.
Cílový název odvoď z adresáře projektu (`job-springwalk` → `springwalk.html`).

**Existuje-li cíl už, nikdy ho nepřepisuj naslepo.** Porovnej oba soubory: často je
ten na webu starší verze s jinou sadou sekcí a chce se doplnit, ne nahradit.

```bash
grep -o 'section id="[a-z0-9-]*"' <zdroj> | sed 's/.*id="//;s/"//' | tr '\n' ' '
grep -o 'section id="[a-z0-9-]*"' web/site/hosted/<projekt>.html | sed 's/.*id="//;s/"//' | tr '\n' ' '
```

Liší-li se, řekni uživateli co, a zeptej se, jestli doplnit nebo nahradit.

### 2. Prověř osobní údaje (povinné, nepřeskakovat)

**Web je veřejný.** Dokumenty z projektů běžně obsahují data klientů a jejich zákazníků.
Projdi zdroj a vypiš, co jsi našel:

- jména fyzických osob, adresy, telefony, e-maily, data narození
- spisové značky, čísla smluv, variabilní symboly, čísla účtů
- konkrétní částky vázané na osobu
- screenshoty z cizích systémů (ty na web nedávej vůbec)

Nález uživateli **ukaž a nabídni anonymizaci**. Při anonymizaci nahrazuj tak, aby text
dál dával smysl: jméno za běžné české příjmení, čísla za `XXXX`, částky zaokrouhli,
konkrétní datum za měsíc. Do dokumentu přidej callout, že jde o anonymizovanou ukázku.

Plná verze zůstává ve zdrojovém adresáři v repu (ten je privátní).

### 3. Zkontroluj mobil

Report se čte na telefonu. Než to pustíš ven, ověř v CSS:

- `meta viewport` je na místě,
- navigace na mobilu nepoužívá `flex-wrap` nad blokovými skupinami (rozbije je, ony se
  stanou jedním flex itemem) — použij `grid`,
- dotykové cíle mají aspoň 44 px,
- tabulky jsou v `.tablewrap{overflow-x:auto}`,
- `overflow-wrap:break-word` na `body`.

### 4. Viditelnost a zápis do evidence

Default pro novou stránku je **mimo vyhledávače** — do `<head>` patří:

```html
<meta name="robots" content="noindex, nofollow" />
```

Do `../sitemap.xml` jde stránka jen tehdy, když uživatel řekne, že má být veřejně
k nalezení. `noindex` a `Disallow` v `robots.txt` nekombinuj: `Disallow` zakáže
stránku vůbec stáhnout, takže robot `noindex` uvnitř neuvidí.

Pak přidej nebo aktualizuj řádek v tabulce v `web/site/hosted/README.md` — adresa,
soubor, zdrojový projekt a cesta, datum překlopení (`DD-MM-YYYY`), viditelnost.
Bez toho za rok nepoznáš živou stránku od zapomenutého exportu.

### 5. Vlož, projev, pushni

Po vložení sekcí zkontroluj, že **pořadí v navigaci sedí s pořadím sekcí** a že čísla
v `<span class="n">` navazují. Prezentační režim je na pořadí navázaný.

```bash
~/ai-prompts-and-skills/shared-skills/_shared/serve.sh <cesta k web/site/hosted> <projekt>.html
```

Odkaz pošli uživateli ke kontrole. Teprve pak commit a push na `main`.

### 6. Ověř, že je to venku

Nestačí, že push prošel. **Ověř obsahem, ne textem, který může být i ve staré verzi** —
hledej `section id="<nová sekce>"`, ne nadpis:

```bash
for i in $(seq 1 24); do
  curl -s https://www.buildai.cz/<projekt> | grep -q 'section id="<nova-sekce>"' && { echo NASAZENO; break; }
  sleep 5
done
```

Nakonec projeď nasazenou stránku na osobní údaje ještě jednou a výsledek uživateli napiš.

---

## Na co narazíš

- **„Na webu to není."** Skoro vždy to znamená, že se editoval soubor v adresáři
  projektu, ale ne ten v `web/site/hosted/`. Jsou to dva různé soubory, push
  zdrojového s webem nic neudělá.
- **Falešně potvrzené nasazení.** Hledáš-li na stránce běžné slovo, najdeš ho i ve
  staré verzi. Porovnej velikost souboru, nebo hledej `id` nové sekce.
- **Railway deploy nespouštěj ručně.** Push na `main` ho spustí sám. `railway up`
  ani redeploy z CLI bez výslovného pokynu uživatele nedělej.
