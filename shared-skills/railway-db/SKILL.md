---
name: railway-db
description: Práce s PostgreSQL databází na Railway pro spread-monitor. Použij když uživatel říká "zkontroluj databázi", "kolik dat je na Railway", "migruj data", "smaž data", "vyexportuj data", nebo "co je v Railway DB".
allowed-tools: Bash, Read, Glob
---

# Railway DB — Spread Monitor

## DŮLEŽITÉ: Po každém nasazení push stará data

**Railway PostgreSQL je ephemeral** — při každém novém deployi nebo restartu Postgres service se DB může vyprázdnit. Lokální `spreads.db` (SQLite) je vždy primární zdroj dat.

**Postup při každém deployi nebo když dashboard nezobrazuje data:**

1. Zkontroluj kolik dat je v Railway DB (viz níže)
2. Pokud 0 nebo výrazně méně než lokálně → spusť migraci
3. Migrace je bezpečná — `/api/ingest` vždy přidává záznamy, nemaže

Toto se stalo opakovaně v historii projektu — vždy bylo nutné znovu pushovat data po deployi.

---

## Připojení

Railway PostgreSQL je přístupná pouze přes ingest API nebo psycopg2 z lokálního Python skriptu s DATABASE_URL.

**DATABASE_URL** je uložena jako Railway env var — není v žádném lokálním souboru.
Získej ji přes GraphQL API:

```bash
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer aeb0bf3e-0564-466f-8ddd-732b4c9e6afd" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ variables(projectId: \"REDACTED_PROJECT_ID\", environmentId: \"REDACTED_ENV_ID\", serviceId: \"REDACTED_SERVICE_ID\") { name value } }"}'
```

Nebo použij veřejné API endpointy (nevyžadují DATABASE_URL):

```bash
# Počet instrumentů
curl -s -u admin:_ZygdWzpSKrNjV_BijvdCg https://web-production-be6f24.up.railway.app/api/averages-all | python -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d)} instrumentů')"

# Posledních 10 záznamů
curl -s -u admin:_ZygdWzpSKrNjV_BijvdCg "https://web-production-be6f24.up.railway.app/api/latest?limit=10"

# Data pro konkrétní symbol (24h)
curl -s -u admin:_ZygdWzpSKrNjV_BijvdCg https://web-production-be6f24.up.railway.app/api/history/EUR?hours=24
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
| DASHBOARD_USER | admin |
| DASHBOARD_PASS | _ZygdWzpSKrNjV_BijvdCg |
| INGEST_API_KEY | dffea339fa4478b22bb2827dce5be662af3ea9c740d083a9 |

## Časté operace

### Kolik dat je v Railway DB?

```bash
curl -s -u admin:_ZygdWzpSKrNjV_BijvdCg https://web-production-be6f24.up.railway.app/api/averages-all | python -c "
import sys, json
d = json.load(sys.stdin)
total = sum(r['samples'] for r in d)
print(f'{len(d)} instrumentů, {total} záznamů celkem')
for r in d:
    print(f'  {r[\"label\"]}: {r[\"samples\"]} vzorků, avg={r[\"avg_spread\"]:.6f}')
"
```

### Migrace z lokálního SQLite na Railway

```python
import sqlite3, httpx
from pathlib import Path

conn = sqlite3.connect(Path('spreads.db'))
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT symbol, label, sec_type, bid, ask FROM spreads WHERE bid IS NOT NULL AND ask IS NOT NULL ORDER BY recorded_at").fetchall()
print(f"Lokálně: {len(rows)} záznamů")

URL = "https://web-production-be6f24.up.railway.app/api/ingest"
KEY = "dffea339fa4478b22bb2827dce5be662af3ea9c740d083a9"

ok = 0
for r in rows:
    resp = httpx.post(URL, json={"symbol": r["symbol"], "label": r["label"], "sec_type": r["sec_type"], "bid": r["bid"], "ask": r["ask"]}, headers={"x-api-key": KEY}, timeout=10)
    if resp.status_code == 200:
        ok += 1
    if ok % 100 == 0 and ok > 0:
        print(f"  {ok}/{len(rows)}...")

print(f"Hotovo: {ok} OK")
```

Spusť jako inline Python skript přes `python - << 'EOF' ... EOF`.

### Přímé SQL přes psycopg2

Pokud potřebuješ přímý SQL přístup, získej DATABASE_URL přes GraphQL (viz výše) a pak:

```python
import psycopg2, os
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM spreads")
print(cur.fetchone())
```

## Kdy Railway DB bývá prázdná

Railway PostgreSQL se resetuje pokud:
- Postgres service byl smazán a znovu vytvořen
- Free tier překročil limity a DB byla pozastavena

**Fix:** Spusť migraci z lokálního SQLite (viz výše). Lokální `spreads.db` je vždy primární zdroj dat.

## Struktura tabulky spreads

```sql
CREATE TABLE spreads (
    id        SERIAL PRIMARY KEY,
    symbol    TEXT NOT NULL,       -- např. 'EUR', 'XAUUSD'
    label     TEXT NOT NULL,       -- např. 'EUR/USD', 'XAUUSD CFD'
    sec_type  TEXT NOT NULL,       -- 'CASH', 'CFD', 'FUT', 'UNKNOWN'
    bid       REAL,
    ask       REAL,
    spread    REAL,                -- ask - bid, zaokrouhleno na 6 des. míst
    recorded_at TIMESTAMP NOT NULL
);
```
