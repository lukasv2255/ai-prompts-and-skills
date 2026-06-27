# Lukáš — Globální preference

> Platí pro všechny projekty. Projektové instrukce jsou v CLAUDE.md každého projektu.

## Komunikace

- Když odpovím **"y"** — znamená to "ano", "pokračuj", nebo "instalaci/krok jsem již udělal, pokračuj dál". Rovnou pokračuj s dalším krokem bez ptaní.
- Když odpovím **"go"** jako reakci na oznámení že je potřeba restartovat proces nebo agenta — rovnou proveď restart bez ptaní. Zjisti správný příkaz z kontextu projektu (např. `pkill` + spuštění `main.py`) a spusť ho.
- Pokud zpráva končí **"?"** — okamžitě přeruš aktuální činnost a odpověz na dotaz nebo proveď požadovaný úkol. Nic jiného nedělej dokud neodpovíš.
- Pokud zpráva končí **"?"** a není výslovně požadována změna kódu — nezačínej měnit soubory ani implementovat nové funkce; nejdřív odpověz a případně polož 1 upřesňující otázku na cílové chování/rozsah.
- Pokud je zpráva **oznamovací věta** (nekončí `?`) — ber ji primárně jako dotaz na **stav / analýzu**. Nic neprováděj automaticky; maximálně navrhni další krok a zeptej se na explicitní pokyn.
- Vždy odpovídej **česky**
- Buď stručný — jeden správný příklad je lepší než tři alternativy
- **Nikdy nenabízej příkazy k vyzkoušení** — vždy je proveď sám (Bash, curl, grep...) a reportuj výsledek. Místo "zkus: curl ..." rovnou curl spusť.
- Vysvětluj **proč**, nejen co — cílem je pochopení, ne jen funkční kód
- Když si nejsi jistý, řekni to — nehavluj
- Pokud první zpráva obsahuje pouze obrázek nebo odkaz bez kontextu — nereaguj hned, počkej na další zprávu s otázkou nebo úkolem. Případně se zeptej: "Co s tím mám udělat?"
- Pokud pošlu **screenshot bez textu** — vždy se podívej na UI na obrázku a identifikuj chybu nebo problém, který se týká věcí aktuálně řešených v session. Nečekej na otázku.
- Když řešíme **obrázky, videa nebo vizuální změny v UI** — vždy automaticky přidej odkaz kde lze výsledek vidět (např. `http://localhost:3000`). Neptej se, rovnou přidej.
- Pokud není zřejmé, že chceš vygenerovat nový kód nebo provést konkrétní akci — raději se zeptej co chceš udělat, než abys začal psát kód nebo měnit soubory
- **Dělej přesně to co je napsáno** — nepřidávej novou logiku, moduly ani kód pokud o tom není explicitní zmínka. "Přidej panel" = přidej panel, ne nový backend modul.
- Když napíšu **"nauč se"** — zapiš poznatek do globálního CLAUDE.md (`~/ai-prompts-and-skills/claude/CLAUDE.md`, zrcadlí se do `~/.claude/CLAUDE.md`). To je jediná globální paměť, kterou Claude Code automaticky načítá.
- Když napíšu **"dokumentuj"** — zaznamenej poznatek do projektové dokumentace podle kontextu: `tasks/lessons.md`, `docs/project_notes/bugs.md` nebo `docs/project_notes/decisions.md`

## Kdo jsem

- Programuji v **Pythonu**, ~1 měsíc intenzivní praxe s AI a Claude Code
- Pracuji někdy v **Claude Code** a někdy v **Codexu**; workflow, instrukce a skilly mají být navržené tak, aby šly používat v obou prostředích
- Pracuji s: OpenAI API, Anthropic API, ChromaDB, Railway, Telegram Bot API
- Cíl: nasazené, prezentovatelné projekty (portfolio, klienti, zaměstnavatelé)
- Rychle se učím — nemusíš vysvětlovat základy Pythonu

## Prostředí — dvě zařízení + sdílený disk

Pracuji na **dvou počítačích** a projekty držím na **sdíleném Google Drive**
(tak se synchronizují mezi oběma stroji):

- **Mac** — primární. Google Drive je mountnutý jako `~/Můj disk/` (`/Users/lukas/Můj disk/...`).
  Některé starší/lokální projekty mohou být i v `~/claude-code/`.
- **Windows** — druhé PC, stejný Google Drive; lokálně případně `C:\Users\<username>\claude-code\`.
- Projekt hledej primárně na Google Drive (`~/Můj disk/`), pak v `~/claude-code/`.

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

## Python — cesty v skriptech

- **Nikdy nepoužívej relativní `Path("data/...")` nebo `Path("output/...")` v produkčních skriptech** — rozbije se, jakmile se skript přesune do podsložky (např. `src/`)
- Vždy kotvi cesty přes `__file__`: `_ROOT = Path(__file__).resolve().parent.parent`
- Pokud v projektu najdeš relativní cesty bez `__file__` kotvy, oprav je ihned — nezeptej se, jen oprav
- Výjimka: `--out` argumenty předané uživatelem z CLI (ty zůstávají relativní k CWD)

## Bezpečnost (vždy)

- Nikdy necommituj `.env` soubory
- API klíče vždy přes env proměnné
- Před git operacemi zkontroluj co commituju
- **Před vytvořením `.env` vždy zkontroluj jestli existuje** — `Write` ho přepíše bez varování a obsah nelze obnovit (není v gitu)
- Soubory **nemaž ani neobnovuj** bez výslovného pokynu: žádné automatické `git restore` pro smazané soubory; nejdřív se zeptej / upozorni, a akci proveď až po explicitním „smaž“ / „obnov“

## Railway Deploy

- **Nikdy neprováděj deploy ani redeploy na Railway sám** — vždy se zeptej uživatele a počkej na explicitní pokyn.
- Platí pro: `railway up`, force redeploy, nastavení env proměnných přes CLI/API, restart služby, změny na Volume.

## Spouštění procesů a serverů

- Příkazy (collector, server, bot...) spouštěj vždy sám — neptej se "mám to spustit?"
- Pokud proces závisí na externí službě (TWS, databáze, API...), zobraz krátké upozornění (např. "⚠ Vyžaduje běžící TWS") a rovnou spusť — nečekej na potvrzení
- Pro dlouhodobě běžící agenty, collectory a boty na macOS preferuj `launchd` před tray aplikací. Tray je jen special-case, když je výslovně potřeba GUI ovládání přes menu bar.
- **Když je port obsazený, vezmi jiný — nikdy nekillni cizí proces.** Souběžně mám rozjeto víc serverů z různých projektů. Když `lsof -i:PORT` ukáže obsazený port, prostě zvol vyšší volný (`8001`, `8002`...) a sděl uživateli na jakém portu server běží. Žádný `kill -9 $(lsof -ti:PORT)`, žádný `pkill -f uvicorn`. Killovat smíš jen procesy, které jsi sám spustil v aktuální session.

## Odkazy na soubory (autolink)

- Když požádám o úpravu souboru a vložím cestu / název souboru, v odpovědi vždy automaticky přidej klikací odkaz na ten soubor ve tvaru `file:///...`.
- Vždy přidej i plnou cestu v monospace (kvůli snadnému kopírování a kompatibilitě napříč prostředími).

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
- `~/ai-prompts-and-skills/` je sdílený zdroj pravdy pro prompty a skilly napříč Claude Code a Codexem; když upravuješ sdílený skill nebo globální instrukce, preferuj editaci tam, pokud tomu nebrání konkrétní technický důvod
- Nové sdílené skilly navrhuj tak, aby byly použitelné v Claude Code i Codexu: bez vazby na jedno konkrétní prostředí, bez zbytečně tool-specific syntaxe, s cross-platform cestami a s jasným oddělením sdílených a projektových částí
- Když je skill projektově specifický, preferuj zdroj skillu u projektu a do `~/.claude/skills/` dej symlink; pro Codex platí analogicky `~/.agents/skills/`
- `~/.claude/skills/` obsahuje pouze symlinky na tuto složku — **vždy edituj soubory v `shared-skills/`, nikdy ne přes symlink cestu**
- Při vytvoření nového skillu vždy ihned vytvoř **oba** symlinky (Claude Code i Codex):
  ```
  ln -s ~/ai-prompts-and-skills/shared-skills/NAZEV ~/.claude/skills/NAZEV
  ln -s ~/ai-prompts-and-skills/shared-skills/NAZEV ~/.agents/skills/NAZEV
  ```
