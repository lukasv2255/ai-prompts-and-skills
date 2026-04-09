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

## Přístup k práci

- Preferuji **jedno správné řešení** před výběrem z pěti možností
- Každý projekt musí být nasazený a funkční — ne jen proof-of-concept
- Jednoduchost nad složitostí — méně kódu, které funguje
- Kód musí být čitelný po měsíci bez kontextu

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

**Fáze 1 — Pochop systém**
- Nakresli pipeline: `[Vstup A] → [Zpracování] → [Výstup]`
- Identifikuj všechny externí služby (API, databáze, scrapy)

**Fáze 2 — Zmapuj přístupy k externím službám**
- Tabulka: Služba | Přístup (✅/❌/❓) | Jak obejít bez přístupu
- Přístup určuje pořadí kroků a co lze testovat bez závislostí

**Fáze 3 — Urči správné pořadí kroků**
- DB schema vždy první
- Vstupy před zpracováním (nejdřív získej data, pak analyzuj)
- Logika před integrací (otestuj výpočty izolovaně)
- Deployment vždy poslední a volitelný

**Fáze 4 — Pro každý krok rozpiš:**
- Co se staví (soubor + jednověté shrnutí)
- Proč v tomto pořadí
- Potenciální problémy + řešení
- Testovací strategie bez externích závislostí
- Blocker (co musíš mít/rozhodnout než začneš)

**Testovací strategie podle typu závislosti:**
| Závislost | Jak testovat |
|---|---|
| DB | SQLite lokálně |
| Externí feed/API | statický soubor `fixtures/` |
| Scraping | HTML snapshot v `fixtures/` |
| Placené API | mock server (FastAPI localhost) |
| Produkční systém | DRY_RUN mode |
| Produkční API (test) | jeden testovací záznam |

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
