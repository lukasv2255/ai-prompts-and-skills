---
name: company-research
description: >
  Deep research na firmu, kam se hlásím (životopis / cold nabídka), s cílem pochopit,
  jak reálně dělá byznys, a připravit kalibrovaný úhel žádosti. Výstup není shrnutí
  firmy, ale pracovní kontext: co prodává, komu, jak vydělává, kde to drhne, kam do
  toho sedím. Umí i doručit důkaz (ukázka práce) a vizuál laděný do značky firmy.

  Použij kdykoliv uživatel říká:
  - "deep research na firmu" / "prozkoumej firmu X"
  - "hlásím se do X, pochop jak dělají byznys"
  - "připrav mi podklad k žádosti do X"
  - "/company-research X"

---

# company-research — deep research firmy k žádosti

Cíl: než pošlu CV nebo cold nabídku, pochopit firmu tak, abych **nepsal do prázdna**.
Metodika navazuje na `cv/sablona-zadosti.md` v projektu AI-brand (sekce B5–B10) — tady
je zabalená do opakovatelného postupu.

Klíčové pravidlo celého skillu: **nejsi rešeršní papoušek.** Fakta oddělíš od domněnek,
čísla opřeš o zdroj, a poctivě přiznáš, co nevíš. To je rozdíl mezi „AI výtahem“ a
podkladem, který obstojí před skeptikem.

---

## Vstup

- Jméno firmy + odkaz (web, inzerát, LinkedIn).
- Typ role: **AI-first** (kde je „stavění s AI“ součást práce), nebo **klasická**
  (junior, wealth management, provoz…). Když to není zřejmé, zeptej se — mění to výstup.

## Postup

### 1. Sběr (WebSearch + WebFetch)

- Web firmy + inzerát → co prodává, komu, jak o tom mluví.
- **Rozhovory zakladatelů / tisk** — tady je reálná mechanika byznysu, ne homepage marketing.
  Hledej: „{firma} rozhovor strategie“, „{zakladatel} {obor}“, výroční zprávy, oborový tisk.
- Tým a jména (kdo rozhoduje, kdo je adresát), advisory board, mateřská/sesterská firma.
- Když je materiálu moc → scraping do Markdownu.

### 2. Syntéza — ne shrnutí, ale pracovní kontext

Sepiš `research.md` do složky žádosti (`cv/job-<slug>/research.md`) s těmito bloky:

- **Jak reálně dělají byznys** (ne jak to vypadá z homepage) — model, funnel, jak vydělávají.
- **Strategie / co dělají vs. co vědomě NEdělají** — druhé je často důležitější (viz níže).
- **Čísla — oddělená FAKTA vs. HYPOTÉZY.** Když si zdroje protiřečí, napiš to a označ „ověřit“.
- **Tým a lidé** (adresát mailu).
- **Jejich moat** — ideálně jejich vlastními slovy z rozhovoru.
- **Přiznané mezery / rizika.**
- **Kam do toho sedím** (viz kalibrace).
- **Otevřené otázky před odesláním** (checklist).
- **Zdroje** (odkazy).

### 3. Kalibrace úhlu — NEJdůležitější krok

Podle typu role se zásadně liší, co s researchem uděláš:

- **AI-first role:** research → **prezentovaný výstup** (návrh zlepšení / příležitosti).
  Šířka (3–5 příležitostí s prioritou) NEBO hloubka (1 rozpracovaná). Nikdy dlouhý seznam bez priorit.
- **Klasická / seniorní / UHNWI role:** research je **skrytý nástroj, ne prezentovaný výstup.**
  Nevyžádaný „návrh, jak zlepšit vaše fungování“ od juniora = přešlap. Úhel není
  „co děláte špatně“, ale **„kde je ve vašem modelu mezera, do které sedím / co můžu odbavit“**
  — nabídka, ne kritika. AI drž jako tiché nářadí, ne jako pitch.

Nejsilnější nález bývá **„co firma vědomě NEdělá“** — když tvoje nabídka míří přesně
na věc, kterou neprodávají (protože si ji klient zařídí sám), je to slabá karta.
Otoč ji: ukaž, že to víš, a nabídni to, co jim reálně chybí.

### 4. (Volitelně) Důkaz místo tvrzení — ukázka práce

U rolí, kde jde o konkrétní dovednost, vyrob **malý reálný artefakt**, který tu dovednost
předvede (např. member-facing brief, due-diligence výtah, analýza). Struktura ukázky, která
dokazuje, že to není jen AI výtah:

- **Signál vs. šum** — vytáhni věc, co v titulku není vidět (rozpor v číslech, skryté riziko).
- **Oddělené fakta / můj odhad / co bych ověřil dál** — falsifikovatelnost.
- **Poznámka k metodě** — kde dělala AI (sběr, první třídění) a **kde rozhodoval člověk**
  (výběr signálu, interpretace, poctivé přiznání limitů). To je ta nedelegovatelná část.
- Čísla vždy se zdrojem a datem.

### 5. (Volitelně) Vizuál laděný do značky firmy

Když artefakt dostane HTML podobu: **odvoď design od značky firmy, ne z AI šablony.**
- Stáhni web firmy, vytáhni reálné tokeny: `curl` → grep na hex barvy a `font-family`.
- Postav self-contained HTML (Google Fonts, print styly pro PDF přes Cmd+P).
- AI-slop check: žádná nekonečná mřížka stejných karet, generické gradienty, zaměnitelný
  SaaS look. Barvy a typo musí mít vztah ke značce.
- Servíruj na localhostu (volný port mimo 8080–8089), pošli klikací odkaz. Nikdy `file://`.

## Výstupy (co je „hotovo“)

Ve složce `cv/job-<slug>/`:
- `research.md` — pochopení firmy (vždy).
- upravený `motivacni-dopis.txt` / `cv` na kalibrovaný úhel (když o to uživatel požádá).
- ukázka práce (`ukazka-*.md` / `.html`) — když role stojí na konkrétní dovednosti.

## Anti-vzory

- Shrnutí firmy místo pracovního kontextu.
- Nevyžádaný „návrh na zlepšení“ u klasické/seniorní role.
- Čísla bez zdroje nebo bez oddělení fakt/hypotéza.
- HTML z generické šablony bez vztahu ke značce firmy.
- Nabízet věc, kterou firma vědomě neprodává.
