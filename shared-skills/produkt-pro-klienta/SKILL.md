---
name: produkt-pro-klienta
description: >
  Hloubková analýza jednoho z mých projektů (dashboard, agent, nástroj) jako produktu
  pro konkrétního klienta. Neprodává moje výsledky, prodává PROCES: jak nástroj
  vede od otázky přes měření k rozhodnutí a pojistce, doložené případy, kde ten cyklus
  reálně doběhl. Výstupem je HTML: cyklus, 2–3 uzavřené případy, otázky klienta →
  funkce, přenos na provoz klienta (hypotéza), formy spolupráce a „Co ve zdrojích není".
  Prodává, ale nic si nevymýšlí.

  Použij kdykoliv uživatel říká:
  - "udělej analýzu <projektu> pro <klienta>"
  - "ukaž, jak můj <dashboard/nástroj> řeší problémy <klienta>"
  - "potřebuju to prodat jako produkt" / "prodejní analýza"
  - "/produkt-pro-klienta <projekt> <klient>"
---

# produkt-pro-klienta — můj projekt jako produkt pro konkrétního klienta

Cíl: klient po přečtení ví, **jakou svou otázku** by s tím nástrojem zodpověděl, a vidí,
**jak** nástroj funguje a že to funguje. Prodává konkrétnost, ne přívlastky.

**Hlavní pravidlo: ukaž proces, ne moje výsledky.** Dokument nemá dokazovat, že jsem
úspěšný (ziskový trader, výkonný obchodník…). Má ukázat cyklus otázka → měření →
zjištění → změna → pojistka v nástroji → nové měření. Čísla slouží jen jako diagnostika
(„ukázalo to slabé místo X"), nikdy jako výkonnost. Žádné celkové zisky, profit factor,
obrat, částky v Kč. Poměry a podíly ano.

Vzorový výstup: `AI-brand-me/job-zephyr/docs/journaling/dashboard-analyza.html`
(trading dashboard pro Zephyr Trade).

## Vstup

- **Projekt** — cesta ke kódu (hledej v `~/<projekt>`, starší věci v `~/muj-brand-archiv/`).
- **Klient** — firma / člověk. Když existuje `research.md` (z `deep-research`), použij ho.
  Když neexistuje a klient není zřejmý z kontextu, zeptej se, jestli nejdřív pustit
  `deep-research`. Bez obrazu klienta je mapování na problémy jen hádání.
- **Kam uložit** — složka u klienta (např. `job-<klient>/docs/<téma>/`). Bez pokynu se zeptej.

## 1. Inventura projektu (read-only)

Nic v projektu neměň. Jen čti a spouštěj read-only výpočty.

1. `CLAUDE.md`, `README.md`, `docs/` — co projekt umí podle autora.
2. Vstupní body: API routy (`grep "@app\.(get|post)"`), panely a záložky v UI, CLI skripty.
3. Docstringy hlavních modulů. Často přesně říkají, na jakou otázku modul odpovídá.
4. Datová vrstva: tabulky, počty řádků, časový rozsah, pokrytí sloupců.
5. Automatizace a integrace: import, alerty, napojení na externí systémy.
6. Kvalita: testy, audit log, validace. Hodí se do sekce „Pod kapotou".

Výstup kroku: seznam funkcí, u každé jedna věta „na jakou otázku odpovídá".

## 2. Uzavřené cykly (nejsilnější důkaz)

Najdi 2–3 případy, kde nástroj vedl k reálné změně. Hledej v `docs/` (rozbory, snapshoty
„před změnou"), `tasks/lessons.md`, plánech a pravidlech, git logu a poznámkách
s hypotézami. Každý případ musí mít doložené všechny 4 kroky:

| Otázka | Měření (z čeho) | Zjištění (číslo) | Změna + pojistka (kde v nástroji) |

- Když chybí doložená změna, případ nepoužívej nebo napiš poctivě „stav před změnou
  zamražen, nové pravidlo se změří proti němu".
- **Nevykládej symboly a značky, které autor nepopsal** (emoji v plánu, barvy, zkratky).
  Když význam není nikde napsaný, nepoužívej to, nebo se zeptej.

## 3. Diagnostická čísla

Ke každé funkci **jedno konkrétní číslo** z reálných dat, spočítané enginem projektu
(ne ručně, ne odhadem).

- Spouštěj existující výpočetní funkce projektu (např. `compute_overview(...)`), ať čísla
  sedí s tím, co ukazuje UI.
- **Poctivý vzorek.** Když data míchají reálné a hypotetické záznamy (zmeškané, simulované,
  testovací), hlavní čísla počítej jen z reálných. Hypotetické ukaž zvlášť a pojmenuj je.
- Když funkce číslo nemá (kalkulačka, integrace), napiš, z čeho vychází. Číslo nevymýšlej.
- Datum dat uveď (dd-mm-yyyy).

## 4. Mapování na problémy klienta

Každá další funkce = jedna řada **Otázka klienta → Funkce → Co to ukázalo**:

- **Problém** formuluj jako otázku, kterou si klient klade jeho slovy
  („Pomáhají zásahy do pozic, nebo škodí?"), ne jako vlastnost nástroje.
- **Funkce** — co nástroj dělá, 2–3 věty, bez techniky.
- **Co to ukázalo** — diagnostické číslo z kroku 3 (slabé místo, ne výkon). Když číslo není, řada zůstane bez něj.

Pořadí: od problému, který klienta nejspíš bolí nejvíc, po nejmenší. 6–10 řad,
slabé funkce vynech.

Pak tabulka **„U mě → U vás"**. Co se přenese beze změny a co by se u klienta muselo
postavit jinak (objem, jednotky, zdroje dat, role lidí vs. automatů). Celou sekci označ
štítkem **hypotéza**. Provoz klienta znáš jen z veřejných zdrojů.

## 5. Formy spolupráce

Tři úrovně, od nejlehčí: **know-how** (konzultace, co a jak měřit), **postavím na míru**
(nad jejich daty), **společný návrh** (s jejich lidmi, stavět až po shodě). Uprav podle
klienta, ale drž tři.

## 6. Dokument

HTML do zvolené složky, design podle sekce *Design systém* v `AI-brand-me/CLAUDE.md`
(DM Serif Display / Outfit / JetBrains Mono, bg `#F5F0E8`, primary `#1A4D2E`, bez stínů,
full-bleed hero, funguje na telefonu).

Osnova:
1. **Hero** — jedna věta, na jakou otázku nástroj odpovídá jinak než běžné nástroje
   + 1–2 věty o původu (proč vznikl).
2. **Cyklus** — 4–5 kroků procesu, u každého, kde v nástroji žije.
3. **Uzavřené případy** — 2–3 případy z kroku 2 (otázka / měření / zjištění / změna).
4. **Na jaké otázky odpovídá** — ostatní funkce s diagnostikou.
5. **Rozsah** — dlaždice s rozsahem a kvalitou dat (počty, období, audit, testy), ne výkon.
6. **U vás** (hypotéza).
7. **Formy spolupráce.**
8. **Pod kapotou** — stack, kde běží, komu patří data, testy.
9. **Co ve zdrojích není** — co o klientovi nevíš a na čem nabídka závisí.

Pravidla textu (platí pravidla pro klientské dokumenty z `AI-brand-me/CLAUDE.md`):
- Fakt a konec. Žádné „z toho plyne…", žádné přívlastky („unikátní", „výkonný").
- Prodává číslo a otázka klienta, ne superlativ.
- Rozlišuj: údaj z dat / vlastní úsudek / chybějící informace.
- Žádné citlivé údaje (čísla účtů, ID statementů, jména třetích stran).
- Česky, s diakritikou, data jako dd-mm-yyyy.

## 7. Předání

Naservíruj přes `~/ai-prompts-and-skills/shared-skills/_shared/serve.sh <složka> <soubor>`
a pošli localhost odkaz. Vizuální kontrolu nedělej, tu si udělá uživatel.
Na web (`na-web`) jen na výslovný pokyn. Dokument obsahuje osobní výsledky.
