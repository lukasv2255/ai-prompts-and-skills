# Tommy — Globální preference

> Platí pro všechny projekty. Projektové instrukce jsou v CLAUDE.md každého projektu.

## Komunikace

- Když odpovím **"y"** — znamená to "ano", "pokračuj", nebo "instalaci/krok jsem již udělal, pokračuj dál". Rovnou pokračuj s dalším krokem bez ptaní.
- Pokud zpráva končí **"?"** — okamžitě přeruš aktuální činnost a odpověz na dotaz nebo proveď požadovaný úkol. Nic jiného nedělej dokud neodpovíš.
- Vždy odpovídej **česky**
- Buď stručný — jeden správný příklad je lepší než tři alternativy
- Vysvětluj **proč**, nejen co — cílem je pochopení, ne jen funkční kód
- Když si nejsi jistý, řekni to — nehavluj
- Pokud první zpráva obsahuje pouze obrázek nebo odkaz bez kontextu — nereaguj hned, počkej na další zprávu s otázkou nebo úkolem. Případně se zeptej: "Co s tím mám udělat?"

## Kdo jsem

- Programuji v **Pythonu**, ~1 měsíc intenzivní praxe s AI a Claude Code
- Pracuji s: OpenAI API, Anthropic API, ChromaDB, Railway, Telegram Bot API
- Cíl: nasazené, prezentovatelné projekty (portfolio, klienti, zaměstnavatelé)
- Rychle se učím — nemusíš vysvětlovat základy Pythonu

## Prostředí — dvě zařízení

Pracuji na **dvou počítačích**:

- **Mac** — primární, cesta projektů: `~/claude-code/`
- **Windows** — druhé PC, cesta projektů: `C:\Users\tommy\claude-code\`

**Pravidla pro cesty v kódu a skillech:**

- Nikdy nepoužívej hardcoded absolutní cestu pro jedno zařízení
- Vždy používej `os.path.expanduser("~")` nebo relativní cesty
- Pokud skill nebo kód vyžaduje cestu k projektu, zjisti aktuální OS: `platform.system()` → `"Darwin"` = Mac, `"Windows"` = Windows
- Při scaffoldu nebo generování cest vždy nabídni variantu pro obě zařízení nebo použij cross-platform zápis

## Přístup k práci

- Preferuji **jedno správné řešení** před výběrem z pěti možností
- Každý projekt musí být nasazený a funkční — ne jen proof-of-concept
- Jednoduchost nad složitostí — méně kódu, které funguje
- Kód musí být čitelný po měsíci bez kontextu
- **Ukazuj průběh** — při delším úkolu průběžně reportuj co děláš, ne až na konci
- **Testuj po každém kroku** — po každé změně ověř že funguje, nespoj víc kroků bez ověření

## Bezpečnost (vždy)

- Nikdy necommituj `.env` soubory
- API klíče vždy přes env proměnné
- Před git operacemi zkontroluj co commituju

## Spouštění procesů a serverů

- Příkazy (collector, server, bot...) spouštěj vždy sám — neptej se "mám to spustit?"
- Pokud proces závisí na externí službě (TWS, databáze, API...), zobraz krátké upozornění (např. "⚠ Vyžaduje běžící TWS") a rovnou spusť — nečekej na potvrzení

## Konfigurace a CLAUDE.md soubory

- Existují pouze dva typy CLAUDE.md: **globální** (`~/.claude/CLAUDE.md`) a **projektový** (v kořeni projektu)
- **Nikdy nevytvářej** `CLAUDE.local.md` ani žádnou lokální variantu vázanou na konkrétní počítač — je to zbytečné a žádná nastavení ani skills se takhle nevytvářejí
- Kdykoliv požádám o zapsání do **globálního CLAUDE.md**, znamená to: uprav soubor `~/ai-prompts-and-skills/claude/CLAUDE.md`, poté zkontroluj jestli se změna zrcadlí do `~/.claude/CLAUDE.md` (přes symlink nebo jiný mechanismus), a potvrď mi výsledek

## Task Management

- Netriviální úkol (3+ kroky) → nejdřív plán
- Po každé korekci → zapiš poučení do `tasks/lessons.md` projektu
- Na začátku session → přečti `tasks/lessons.md` pokud existuje
- Vždy používej TodoWrite pro sledování průběhu — aktualizuj po každém dokončeném kroku

## Plánování nového projektu

Před zahájením implementace projdi tyto fáze:

**Fáze 1 — Průzkum** _(vždy specifický pro projekt)_

- Jaký problém firma/uživatel řeší a co teď dělá ručně?
- Nakresli pipeline: `[Vstup] → [Zpracování] → [Výstup]`
- Jaké typy vstupů systém dostává?
- Jaké externí systémy jsou zapojeny? (API, DB, CRM...)
- Kdo bude systém provozovat — vývojář nebo klient sám?

**Fáze 2 — Zmapuj přístupy k externím službám**

- Tabulka: Služba | Přístup (✅/❌/❓) | Jak obejít bez přístupu
- Přístup určuje pořadí kroků a co lze testovat bez závislostí

**Fáze 3 — Architektura** _(kostra stejná, části se mění)_

- Identifikuj pevné části (sdílené mezi projekty) vs. variabilní (mění se per klient)
- Rozhraní vstupního systému = jediný soubor který se mění mezi projekty
- DB schema vždy první, deployment vždy poslední

**Fáze 4 — Knowledge Base / data** _(pokud projekt pracuje s daty klienta)_

- Nejdřív KB, pak kód — agent je tak dobrý jako data která má
- Malá KB → textové soubory v `prompts/`
- Velká KB → vektorová databáze (RAG/ChromaDB)
- `prompts/` = produkční data, `tests/` = simulovaná testovací data (fixtures)

**Fáze 5 — Schvalovací kanál** _(pokud člověk schvaluje výstupy)_

- Vývojář/test → Telegram
- Klient bez IT → Web dashboard
- Firma se Slackem → Slack s tlačítky
- Ověřená produkce → auto-send pro low-risk, schválení jen pro citlivé typy

**Fáze 6 — Chybějící informace**

- Systém neeskaluje rovnou — navrhne výstup nebo se zeptá na doplnění
- Člověk doplní → systém vygeneruje nový výstup ke schválení
- Timeout bez reakce → zalogovat jako `needs_human`

**Fáze 7 — Testování bez reálného prostředí**

- Fixtures = vymyšlená data simulující reálný systém (`tests/`)
- Testovací vstupy = konkrétní případy s očekávaným výsledkem
- Výsledková tabulka: klasifikace správná? Výstup správný? Eskalace správná?

| Závislost            | Jak testovat                    |
| -------------------- | ------------------------------- |
| DB                   | SQLite lokálně                  |
| Externí feed/API     | statický soubor `fixtures/`     |
| Scraping             | HTML snapshot v `fixtures/`     |
| Placené API          | mock server (FastAPI localhost) |
| Produkční systém     | DRY_RUN mode                    |
| Produkční API (test) | jeden testovací záznam          |

**Fáze 8 — Nasazení postupně (shadow mode)**

- `DRY_RUN=true` → jen logy, žádné notifikace
- Shadow mode → systém generuje výstupy, člověk pracuje paralelně, porovnání
- Produkce → nejdřív low-risk typy, pak rozšiřovat

**Fáze 9 — Pricing** _(škáluje podle složitosti integrace)_

- Jednoduchá integrace → nižší setup fee
- Složitá integrace (OAuth, třetí systémy, routing) → vyšší setup fee
- Měsíční provoz = infrastruktura + monitoring + drobné úpravy

**Fáze 10 — Správa po nasazení**

- KB aktualizuje klient nebo vývojář na vyžádání
- Credentials a tokeny mají expiraci → nastavit připomenutí
- Logy monitoruje vývojář, klient hlásí problémy

**Pravidlo deploymentu:** Projekt musí fungovat lokálně před tím než řešíš Railway nebo jiný cloud.

## Skills

- Všechny skilly jsou v `~/ai-prompts-and-skills/shared-skills/`
- `~/.claude/skills/` obsahuje pouze symlinky na tuto složku
- Při vytvoření nového skillu vždy ihned vytvoř symlink: `ln -s ~/ai-prompts-and-skills/shared-skills/NAZEV ~/.claude/skills/NAZEV`

## Visual Review

Po každé změně která ovlivní UI/web:

1. Uprav kód
2. Commitni a pushni na deployment platform (Railway nebo jiná)
3. Počkej na deploy (~60s)
4. Otevři web přes Chrome extension a udělej screenshot
5. Zkontroluj vizuálně a reportuj výsledek
6. Pokud problém přetrvává — postni screenshot do chatu, zkus jiný přístup k opravě a opakuj celý cyklus od kroku 1
