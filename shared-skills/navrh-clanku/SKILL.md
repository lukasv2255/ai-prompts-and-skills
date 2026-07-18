---
name: navrh-clanku
description: "Zpracuje myšlenku, poznámku nebo zážitek z práce do souboru s návrhem článku a uloží ho do C:\\Users\\tommy\\Můj disk\\AI-brand\\AI-brand-me\\writing\\<oblast>/. Použij kdykoliv uživatel řekne 'zapiš návrh na článek', 'navrhni článek', 'udělej z toho článek', 'zpracuj to jako článek', 'zapiš to do writing', nebo 'to by byl dobrý článek'."
---

# Návrh článku

Cílem je **nenechat myšlenku zapadnout**. Uživatel při práci narazí na něco,
co stojí za sepsání — ty to hned převedeš na použitelný podklad pro článek
a uložíš na správné místo.

## Kam se ukládá

Kořen: `C:\Users\tommy\Můj disk\AI-brand\AI-brand-me\writing\`

Soubor: `<oblast>/<slug>.md`

- `<slug>` — krátký, česky, bez diakritiky, kebab-case (`referencni-image-a-prompt`)
- Pokud je obsah vázaný na konkrétní den nebo událost, přidej prefix
  `YYYY-MM-DD-`. Jinak datum nepoužívej.

## Jak vybrat adresář

V tomto pořadí:

1. **Uživatel oblast řekl** → použij ji (i když adresář ještě neexistuje — vytvoř ho).
2. **Myšlenka vznikla v konkrétním projektu** → adresář podle projektu.
   Odvoď z aktuálního working directory nebo z toho, o čem byla session.
3. **Jinak podle tématu obsahu.**

Existující adresáře (zjisti aktuální stav přes `ls`, seznam se vyvíjí):

| Adresář | Co tam patří |
|---|---|
| `project-building/` | stavba projektů, git, workflow, prompty, Claude Code |
| `mail-agent/` | mail agent, cold outreach, automatizace mailu |
| `spread-monitor/` | trading, spready, collector, data |
| `trenzo/` | cyklistika, FTP, TSS/CTL/ATL, tréninkové metriky |
| `AI-visual/` | generování obrázků, reference, vizuální identita |
| `diktafon/` | diktafon, přepis, hlasové workflow |
| `twitter/` | přímo obsah na X, ne dlouhý článek |
| `marketing/` | pozicování, brand, prodej |

Nový adresář zakládej jen tehdy, když se téma opravdu nevejde nikam jinam.
Když si nejsi jistý mezi dvěma, řekni to v odpovědi a jeden vyber — neptej se.

## Formát souboru

````markdown
# <Titulek — konkrétní, ne obecný>

<!--
Typ obsahu: námět na článek
Cíl: co má čtenář po přečtení umět nebo pochopit
Publikační úhel: pro koho to je a proč ho to zajímá
Hlavní claim: jedna věta, kterou článek dokazuje
-->

## Krátká teze

2–4 odstavce. Nejdřív pointa, pak proč to tak je. Tohle musí dávat smysl
i samostatně — často z toho vznikne tweet nebo úvod.

## Hlavní článek

### <podnadpis>

...

### <podnadpis>

...

## Co zkusím příště

Konkrétní další krok nebo otevřená otázka.
````

## Zásady psaní

Platí tone & style z projektového `CLAUDE.md` v AI-brand:

- Česky, stručně, lidsky. Žádné generické AI fráze.
- Píše se to jako **poznámky z praxe**, ne jako návod z internetu:
  co jsem si myslel předtím / co mě překvapilo / co zkusím příště.
- Konkrétní workflow, čísla a příklady před teorií.
- Nevymýšlej si zdroje, čísla ani citace. Když něco nevíš, napiš to do
  souboru jako otevřenou otázku.
- Vytěž maximum z kontextu aktuální session — reálné chyby, slepé uličky
  a co je nakonec vyřešilo. To je hodnotnější než obecný výklad.

## Postup

1. Zjisti myšlenku — z poslední zprávy uživatele nebo z kontextu session.
   Když je zadání jednořádkové, rozveď ho o to, co se v session skutečně stalo.
2. Vyber adresář a slug podle pravidel výše.
3. Zkontroluj, jestli už na téma soubor neexistuje (`ls` daného adresáře).
   Pokud ano — **rozšiř existující soubor**, nezakládej duplicitu.
4. Napiš soubor.
5. Odpověz: cesta k souboru jako klikací odkaz, titulek a jednořádkové
   shrnutí úhlu. Nic dlouhého.

Nepublikuj, necommituj a nikam neposílej — jen ulož soubor.
