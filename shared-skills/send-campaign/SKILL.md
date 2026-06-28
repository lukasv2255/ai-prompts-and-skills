---
name: send-campaign
description: Spustí cold-mailing kampaň přes scripts/send_campaign.py v aktuální mail-agent instanci. Použij když uživatel řekne "send campaign", "spusť kampaň", "pošli leady", případně s modifikátory "live/test/one/fast/dry-run". Pokrývá výběr režimu, kontrolu ready leadů, spuštění s caffeinate na macOS, běh na pozadí a reporting.
---

# Send Campaign

Spustí cold-mailing kampaň v aktuální mail-agent instanci. Skript je vždy v `scripts/send_campaign.py` a používá `src/modules/campaign_db.py` pro načítání leadů z `data/leads.html` (nebo `.csv`) a stavu z `data/sent.db`.

## Detekce projektu

Před akcí ověř že jsi v mail-agent instanci:

```bash
test -f scripts/send_campaign.py && test -f src/modules/campaign_db.py
```

Pokud chybí, zeptej se uživatele na cestu k mail-agent projektu a přejdi tam (`cd`).

## Parsing pokynu

| Uživatel řekne                   | Flagy                                                           |
| -------------------------------- | --------------------------------------------------------------- |
| "send campaign" / "spusť kampaň" | `` (default test mode, vše ready, interval do 18:00)            |
| "...one"                         | `--one` (1 email okamžitě, ignoruje window)                     |
| "...fast"                        | `--fast` (vše během 10 minut)                                   |
| "...week"                        | `--week` (40 mailů/den, max 7 dní, rovnoměrně v okně 06–18 CET) |
| "...live"                        | `--live` (ostrý provoz, jinak test mode na TEST_REDIRECT_EMAIL) |
| "...dry-run" / "...zobraz"       | `--dry-run`                                                     |
| "...report" / "...stav kampaně"  | `--report`                                                      |
| kombinace, např. "one live"      | `--one --live`                                                  |

Flagy lze kombinovat. `--live` je destruktivní (posílá reálné emaily) — pokud uživatel požaduje plný `--live` (bez `--one`), **vždy nejdřív spusť `--dry-run --live`** a ukaž počet leadů + průměrný interval, pak se zeptej na potvrzení.

## Default chování (bez --one/--fast)

Skript rozprostře leady do okna **06:00–18:00 CET** podle aktuálního času:

- Uvnitř window: interval = (do 18:00) / total leadů → kampaň skončí dnes před 18:00
- Mimo window: čeká do 06:00, pak rozprostře přes celých 12 h

Pokud uživatel chce začít teď a je mimo window, upozorni že skript bude čekat do dalšího 06:00.

## Týdenní režim (`--week`)

Použij když uživatel řekne **"send campaign week"** / **"týdenní kampaň"** / `/send-campaign week`:

- Posílá max **40 mailů/den**, max **7 dní**, rovnoměrně v okně 06:00–18:00 CET.
- Denní counter čte z `sent_emails.first_sent_at = dnes` v DB → restart procesu pokračuje od dosaženého počtu (odolné vůči pádu, sleep, killu).
- Když `load_leads()` vrátí 0 ready → kampaň skončí dřív (vyčerpán pool).
- Po naplnění denní kvóty spí do dalších 06:00 CET.
- `--week` nelze kombinovat s `--one` / `--fast` / `--dry-run`.

Spouštění (vždy detached + caffeinate, kampaň běží dny):

```bash
nohup caffeinate -i python3 scripts/send_campaign.py --week --live \
  > logs/campaign/week_$(date +%Y%m%d_%H%M%S).out 2>&1 &
disown
```

Bez `nohup` + `disown` kampaň umře se zavřením shellu/Claude Code session. Upozorni uživatele.

## Spouštění

### macOS — vždy `caffeinate -i`

Default a `--fast` režimy běží hodiny a Mac by mohl jít spát → ztratíš zbytek kampaně. Vždy obal příkaz:

```bash
caffeinate -i python3 scripts/send_campaign.py [FLAGY]
```

`caffeinate -i` brání idle sleepu. **Nezabraňuje lid-close sleepu** — pokud má uživatel MacBook a zavře víko, kampaň spadne. Upozorni na to při dlouhých bězích.

Linux/jiné: pusť bez `caffeinate`.

### Background mode

`--one` a `--dry-run` jsou rychlé → spusť foreground.

Vše ostatní (default, `--fast`, `--live` plné) běží minuty až hodiny → **spusť `run_in_background: true`** a vrať ID. Uživatel dostane notifikaci po dokončení.

### Bezpečnostní pravidla

- **Nikdy nespouštěj plný `--live` bez explicitního pokynu** ("send campaign live" nebo "ano" v reakci na dry-run shrnutí).
- Pokud uživatel řekne jen "send campaign", default je **test mode** (na `TEST_REDIRECT_EMAIL` z `.env`).
- Před plným `--live` ukaž počet leadů z dry-runu, ne spouštěj naslepo.

## Kontrola stavu

### Kolik leadů je ready

```bash
python3 scripts/send_campaign.py --dry-run --live 2>&1 | head -3
```

První řádek: `[DRY-RUN] [LIVE] N leadů, režim: ...`

### Běžící proces

```bash
ps aux | grep -E "send_campaign|caffeinate" | grep -v grep
```

### Tail logu běžícího běhu

Background tool vrací cestu k output souboru — čti přes `tail` nebo `Read`. Pokud potřebuješ historie:

```bash
tail -n 20 logs/campaign/sends.jsonl
```

## Killování běžící kampaně

Skript má SIGTERM handler co čeká na dokončení aktuálního emailu — `kill PID` často neukončí proces pokud čeká na send window. Použij **SIGKILL**:

```bash
ps aux | grep -E "send_campaign|caffeinate" | grep -v grep | awk '{print $2}' | xargs kill -9
```

Před killem upozorni že leady už odeslané zůstanou v DB jako `sent` — restart kampaně je načte už správně (vynechá `sent`, posílá jen `ready`).

## Konflikty paralelních běhů

`campaign_db.py` nemá lock. **Nikdy nespouštěj dva `send_campaign.py` současně** — došlo by k duplikátnímu odeslání leadů co jeden běh už má v paměti ale ještě je nestihl označit `sent`. Vždy nejdřív killni existující proces.

## Report

```bash
python3 scripts/send_campaign.py --report
```

Ukáže celkové odesláno/chyby a posledních 5 záznamů z `logs/campaign/sends.jsonl`.
