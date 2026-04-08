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
