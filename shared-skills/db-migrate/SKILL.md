---
name: db-migrate
description: >
  Přenos dat mezi databázemi: SQLite → PostgreSQL, CSV → DB, DB → DB.
  Zachování timestampů, batch processing, deduplication, progress tracking.

  Použij PROAKTIVNĚ kdykoliv zazní:
  - "přenes data", "migruj data", "záloha databáze"
  - "data zmizela", "DB je prázdná", "obnov data"
  - "kopíruj záznamy z X do Y"
  - "SQLite na Railway", "lokální data na server"
  - "ingest-bulk", "historická data"
---

# Migrace dat mezi databázemi

Odzkoušeno na projektu spread-monitor: 1584 záznamů SQLite → Railway PostgreSQL přes `/api/ingest-bulk`.

---

## Kdy migrovat

- **Po deployi na Railway** — Railway PostgreSQL se občas resetuje; lokální SQLite je primární záloha
- **Nový stroj** — přesuň data z CSV/SQLite na běžící server
- **Spojení dat** — více počítačů sbírá data, chceš je sloučit na jednom místě

---

## Vzor 1: SQLite → Railway API (přes `/api/ingest-bulk`)

Nejbezpečnější způsob — nevyžaduje přímý přístup k PostgreSQL, funguje přes HTTPS.

```python
import sqlite3, httpx

# 1. Načti data z lokální SQLite
conn = sqlite3.connect('spreads.db')
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT symbol, label, sec_type, bid, ask, recorded_at FROM spreads ORDER BY recorded_at ASC"
).fetchall()
conn.close()
print(f"Načteno {len(rows)} záznamů")

# 2. Odešli po batchích (200 = dobrý kompromis rychlost/timeout)
API_URL = "https://xxx.up.railway.app/api/ingest-bulk"
API_KEY = "tvuj_ingest_api_klic"
BATCH   = 200
total   = 0

for i in range(0, len(rows), BATCH):
    batch = [dict(r) for r in rows[i:i+BATCH]]
    r = httpx.post(
        API_URL,
        json=batch,
        headers={"x-api-key": API_KEY},
        timeout=30
    )
    if r.status_code == 200:
        total += r.json()["count"]
        print(f"  batch {i//BATCH + 1}: OK — {total}/{len(rows)} celkem")
    else:
        print(f"  batch {i//BATCH + 1}: CHYBA {r.status_code} — {r.text[:300]}")
        break

print(f"Hotovo: {total} záznamů přesunuto")
```

**Proč batch=200:** Jeden velký request může timeoutnout (Railway má ~30s limit). 200 záznamů / request je spolehlivé.

---

## Vzor 2: SQLite → PostgreSQL přímo (psycopg2)

Pokud máš přímý přístup k DB (lokální vývoj nebo VPN).

```python
import sqlite3, psycopg2
from datetime import datetime

# Zdroj
src = sqlite3.connect('spreads.db')
src.row_factory = sqlite3.Row
rows = src.execute("SELECT * FROM spreads ORDER BY recorded_at").fetchall()
src.close()

# Cíl
DATABASE_URL = "postgresql://postgres:heslo@host:5432/dbname"
ssl = "disable" if "railway.internal" in DATABASE_URL else "require"
dst = psycopg2.connect(DATABASE_URL, sslmode=ssl)

with dst.cursor() as cur:
    for r in rows:
        cur.execute(
            "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            (r["symbol"], r["label"], r["sec_type"],
             r["bid"], r["ask"], r["spread"],
             datetime.fromisoformat(r["recorded_at"]))
        )
dst.commit()
dst.close()
print(f"Přeneseno {len(rows)} záznamů")
```

**`ON CONFLICT DO NOTHING`** — bezpečné opakování, nezduplikuje záznamy pokud migrace proběhla částečně.

---

## Vzor 3: CSV → PostgreSQL

```python
import csv, psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://..."
ssl = "disable" if "railway.internal" in DATABASE_URL else "require"
conn = psycopg2.connect(DATABASE_URL, sslmode=ssl)

with open('data/spreads_backup.csv') as f, conn.cursor() as cur:
    reader = csv.DictReader(f)
    rows = list(reader)
    for r in rows:
        cur.execute(
            "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            (r["symbol"], r["label"], r["sec_type"],
             float(r["bid"]) if r["bid"] else None,
             float(r["ask"]) if r["ask"] else None,
             float(r["spread"]) if r["spread"] else None,
             datetime.fromisoformat(r["recorded_at"]))
        )
    conn.commit()

conn.close()
print(f"Importováno {len(rows)} řádků z CSV")
```

---

## Ověření po migraci

```python
import httpx

r = httpx.get("https://xxx.up.railway.app/api/averages-all", timeout=10)
data = r.json()
total_samples = sum(item["samples"] for item in data)
print(f"{len(data)} symbolů, {total_samples} záznamů celkem")
for item in data:
    print(f"  {item['label']}: {item['samples']} vzorků")
```

---

## Časté chyby při migraci

| Chyba | Příčina | Fix |
|-------|---------|-----|
| `500 Internal Server Error` na `/api/ingest-bulk` | `sslmode="require"` v endpointu hardcoded | Přidej SSL detekci: `"disable" if "railway.internal" in url else "require"` |
| `timeout` při velkém batchi | Railway limit ~30s | Zmenši batch na 100–200 |
| Duplikáty po opakované migraci | INSERT bez kontroly | Použij `ON CONFLICT DO NOTHING` nebo ověř před insertem |
| `datetime.fromisoformat` selhává | SQLite ukládá `2026-04-01T20:38:37` (s T), PostgreSQL čeká jiný formát | `fromisoformat` zvládá oba formáty od Python 3.7+ |
| `ModuleNotFoundError: psycopg2` | Lokálně není nainstalovaný | `pip3 install psycopg2-binary` |

---

## Railway PostgreSQL — SSL pravidlo

```python
# VŽDY toto — nikdy nehardcoduj sslmode="require"
url = os.environ["DATABASE_URL"]
ssl = "disable" if "railway.internal" in url else "require"
conn = psycopg2.connect(url, sslmode=ssl)
```

**Proč:** `postgres.railway.internal` (interní hostname) SSL nepodporuje. Veřejný proxy (`*.railway.app`) SSL vyžaduje. Detekce podle hostnameu funguje vždy.
