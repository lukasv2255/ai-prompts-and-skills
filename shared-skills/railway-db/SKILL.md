---
name: railway-db
description: Práce s PostgreSQL databází na Railway pro spread-monitor. Použij když uživatel říká "zkontroluj databázi", "kolik dat je na Railway", "migruj data", "smaž data", "vyexportuj data", nebo "co je v Railway DB".
allowed-tools: Bash, Read, Glob
---

# Railway DB — Spread Monitor

## DŮLEŽITÉ: Primární zdroj dat jsou CSV soubory

**Zdroj pravdy = `data/*.csv` soubory v projektu** (jeden soubor per instrument, nový formát s label sloupcem).
Railway PostgreSQL obsahuje stejná data + kompletní historii od začátku sběru.

**Postup když dashboard nezobrazuje data:**
1. Zkontroluj kolik dat je v Railway DB (viz níže)
2. Pokud 0 nebo výrazně méně → spusť `migrate_csv_to_railway.py`
3. Migrace přidává záznamy, nemaže — bezpečné spustit opakovaně

---

## Připojení

Railway PostgreSQL je přístupná pouze interně (`postgres.railway.internal`) — zvenčí nelze připojit psycopg2 přímo.
Veškeré operace se provádějí přes HTTP API endpointy.

```bash
# Počet instrumentů a záznamů
curl -s "https://web-production-be6f24.up.railway.app/api/averages-all" | python3 -c "
import sys, json
d = json.load(sys.stdin)
total = sum(r['samples'] for r in d)
print(f'{len(d)} instrumentu, {total} zaznamu celkem')
for r in d:
    print(f'  {r[\"label\"]}: {r[\"samples\"]} vzorku, avg={r[\"avg_spread\"]}')
"

# Posledních 10 záznamů
curl -s "https://web-production-be6f24.up.railway.app/api/latest?limit=10"
```

## IDs pro spread-monitor

| Klíč | Hodnota |
|------|---------|
| Token | aeb0bf3e-0564-466f-8ddd-732b4c9e6afd |
| Project ID | REDACTED_PROJECT_ID |
| Environment ID | REDACTED_ENV_ID |
| Web service ID | REDACTED_SERVICE_ID |
| Postgres service ID | REDACTED_POSTGRES_ID |
| Dashboard URL | https://web-production-be6f24.up.railway.app |
| INGEST_API_KEY | dffea339fa4478b22bb2827dce5be662af3ea9c740d083a9 |

## Migrace CSV → Railway

**Skript:** `C:\Users\tommy\claude-code\spread-monitor\migrate_csv_to_railway.py`

Načte všechny `data/*.csv` soubory (nový formát s label sloupcem) a nahraje je přes `/api/ingest-bulk`.

```bash
cd C:\Users\tommy\claude-code\spread-monitor
python migrate_csv_to_railway.py
```

Skript automaticky:
- Přeskočí soubory ve starém formátu (bez label sloupce)
- Přeskočí řádky s neplatnými hodnotami (bid <= 0, ask <= bid)
- Odesílá po 200 záznamech (batch)
- Zachovává původní `recorded_at` timestampy

## Smazání všech dat v Railway DB

V `main.py` existuje endpoint `POST /api/admin/clear-spreads`:

```bash
curl -s -X POST "https://web-production-be6f24.up.railway.app/api/admin/clear-spreads" \
  -H "x-api-key: dffea339fa4478b22bb2827dce5be662af3ea9c740d083a9"
```

⚠️ **Pozor:** Railway má build cache problém — `main.py` změny se někdy neprojeví ihned.
Pokud endpoint vrací 404, zkus spustit nový deploy:

```bash
# Trigger redeploy
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer aeb0bf3e-0564-466f-8ddd-732b4c9e6afd" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceInstanceRedeploy(environmentId: \"REDACTED_ENV_ID\", serviceId: \"REDACTED_SERVICE_ID\") }"}'
```

## Kompletní reset DB + reingest

```bash
# 1. Smaž všechna data
curl -s -X POST "https://web-production-be6f24.up.railway.app/api/admin/clear-spreads" \
  -H "x-api-key: dffea339fa4478b22bb2827dce5be662af3ea9c740d083a9"

# 2. Nahrај CSV data
cd C:\Users\tommy\claude-code\spread-monitor
python migrate_csv_to_railway.py
```

## Struktura tabulky spreads

```sql
CREATE TABLE spreads (
    id        SERIAL PRIMARY KEY,
    symbol    TEXT NOT NULL,       -- např. 'EUR', 'XAUUSD', 'CL'
    label     TEXT NOT NULL,       -- např. 'EUR/USD', 'XAUUSD CFD', 'Crude Oil (CL)'
    sec_type  TEXT NOT NULL,       -- 'CASH', 'CFD', 'FUT', 'UNKNOWN'
    bid       REAL,
    ask       REAL,
    spread    REAL,                -- ask - bid, zaokrouhleno na 6 des. míst
    recorded_at TIMESTAMP NOT NULL
);
```

## Kdy DB může být prázdná

- Postgres service byl smazán a znovu vytvořen na Railway
- Free tier překročil limity

**Fix:** `python migrate_csv_to_railway.py` — nahraje data z CSV souborů.

## Poznámky k datům

- **Non-forex FUT** (CL, NQ, DAX, MBT, MGC, MCL, MES, SI, ZW, GBL, 1OZ): unikátní symboly → nikdy nebyly smazány cleanup operací → DB má kompletní historii od začátku sběru
- **Forex CASH + forex FUT** (EUR/6E, GBP/6B, atd.): single-letter symboly → byly smazány při cleanup April 2026 → v DB jen data z CSV (April 1–8, 2026)
- **CFD** (XAUUSD, XAGUSD): unikátní symboly → kompletní history v DB
