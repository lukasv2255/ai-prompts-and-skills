# Tommy — Globální preference

> Platí pro všechny projekty. Projektové instrukce jsou v CLAUDE.md každého projektu.

## Komunikace

- Když odpovím **"y"** — znamená to "ano", "pokračuj", nebo "instalaci/krok jsem již udělal, pokračuj dál". Rovnou pokračuj s dalším krokem bez ptaní.
- Když odpovím **"go"** jako reakci na oznámení že je potřeba restartovat proces nebo agenta — rovnou proveď restart bez ptaní. Zjisti správný příkaz z kontextu projektu (např. `pkill` + spuštění `main.py`) a spusť ho.
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
- **Před vytvořením `.env` vždy zkontroluj jestli existuje** — `Write` ho přepíše bez varování a obsah nelze obnovit (není v gitu)

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

## MCP nástroje

- Playwright MCP preferuj před Chrome MCP pro automatizaci prohlížeče.
- **PRAVIDLO: MCP Telegram vůbec neovládá.** Žádné odesílání příkazů, žádné `/check`, `/yes`, `/no` ani nic jiného. Uživatel ovládá Telegram kompletně sám.

## Skills

- Všechny skilly jsou v `~/ai-prompts-and-skills/shared-skills/`
- `~/.claude/skills/` obsahuje pouze symlinky na tuto složku
- Při vytvoření nového skillu vždy ihned vytvoř symlink: `ln -s ~/ai-prompts-and-skills/shared-skills/NAZEV ~/.claude/skills/NAZEV`
