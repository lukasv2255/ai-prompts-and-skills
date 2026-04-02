---
name: railway-collector-app
description: >
  Kompletní šablona a průvodce pro projekty kde: lokální skript sbírá data
  ze zdroje (API, broker, scraper, senzor...) → odesílá HTTPS POST na Railway
  FastAPI server → ukládá do PostgreSQL → web dashboard zobrazuje data s
  automatickým refreshem.

  Použij PROAKTIVNĚ kdykoliv projekt potřebuje:
  - "collector" nebo "sběrač dat" + web dashboard
  - lokální skript odesílá data někam
  - Railway web + PostgreSQL + frontend polling
  - live dashboard ze skriptu/brokera/senzoru
  - vzor: sběr dat → uložení → zobrazení

  Skill obsahuje kompletní scaffolding — vytvoří strukturu projektu, vysvětlí
  Railway setup, a zdokumentuje všechny pasti na které jsme narazili.
---

# Railway Collector App — Šablona projektu

Vzor odzkoušený na projektu **spread-monitor** (IB API → Railway FastAPI → PostgreSQL → dashboard). Níže jsou **konkrétní příkazy a hodnoty** z reálného projektu jako reference.

---

## Architektura

```
LOKÁLNÍ STROJ
┌─────────────────────────────────────────────────────────┐
│  collector.py                                            │
│  • připojí se ke zdroji dat (API, broker, scraper...)   │
│  • sbírá každých N sekund, ukládá do spreads.db (SQLite)│
│  • POST /api/ingest na Railway + x-api-key header       │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTPS POST (každých N sec)
RAILWAY
┌──────────────────────────▼──────────────────────────────┐
│  main.py (FastAPI)                                       │
│  POST /api/ingest        ← přijme data z collectoru     │
│  POST /api/ingest-bulk   ← migrace historických dat     │
│  GET  /api/averages-all  ← frontend polling             │
│  GET  /api/history/{sym} ← detail grafu                 │
│  GET  /                  ← HTML dashboard               │
│              │                        │                 │
│         psycopg2                  Jinja2/HTML           │
│              ▼                        ▼                 │
│  PostgreSQL (railway.internal)    Frontend              │
│  tabulka: spreads                 • JS setInterval 60s  │
│  id, symbol, label, sec_type,     • fetch /api/...      │
│  bid, ask, spread, recorded_at    • render bez reload   │
└─────────────────────────────────────────────────────────┘
```

---

## Struktura projektu

```
projekt/
├── collector.py          # lokální sběrač dat
├── main.py               # FastAPI server
├── database.py           # SQLite (lokální dev/backup)
├── database_pg.py        # PostgreSQL (Railway produkce)
├── config.json           # konfigurace instrumentů/zdrojů
├── requirements.txt      # závislosti collectoru (lokálně)
├── requirements-web.txt  # závislosti serveru (Railway)
├── nixpacks.toml         # říká Railway: použij requirements-web.txt
├── templates/
│   └── index.html        # dashboard frontend
├── .env                  # REMOTE_INGEST_URL + REMOTE_API_KEY
└── data/                 # CSV zálohy dat (verzováno v gitu)
```

---

## Implementace — krok za krokem

### 1. Databázová vrstva

**`database.py`** — lokální SQLite (dev + backup buffer):
```python
import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "spreads.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS spreads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            label TEXT NOT NULL,
            sec_type TEXT NOT NULL DEFAULT 'UNKNOWN',
            bid REAL, ask REAL, spread REAL,
            recorded_at TEXT NOT NULL
        )""")

def insert_spread(symbol, label, sec_type, bid, ask):
    spread = round(ask - bid, 6) if bid and ask else None
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) VALUES (?,?,?,?,?,?,?)",
            (symbol, label, sec_type, bid, ask, spread, datetime.utcnow().isoformat())
        )
```

**`database_pg.py`** — Railway PostgreSQL:
```python
import os
import psycopg2, psycopg2.extras
from datetime import datetime

def get_conn():
    url = os.environ["DATABASE_URL"]
    # KRITICKÉ: railway.internal nepodporuje SSL → disable
    # Veřejný proxy (neon, supabase...) SSL vyžaduje → require
    ssl = "disable" if "railway.internal" in url else "require"
    conn = psycopg2.connect(url, sslmode=ssl)
    conn.autocommit = False
    return conn

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS spreads (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                label TEXT NOT NULL,
                sec_type TEXT NOT NULL DEFAULT 'UNKNOWN',
                bid REAL, ask REAL, spread REAL,
                recorded_at TIMESTAMP NOT NULL
            )""")
        conn.commit()

def insert_spread(symbol, label, sec_type, bid, ask, recorded_at=None):
    spread = round(ask - bid, 6) if bid and ask else None
    ts = recorded_at or datetime.utcnow()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (symbol, label, sec_type, bid, ask, spread, ts)
            )
        conn.commit()
```

**`main.py`** — auto-detekce prostředí:
```python
import os
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    import database_pg as db
else:
    import database as db
```

### 2. Ingest API (main.py)

```python
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()
INGEST_API_KEY = os.environ.get("INGEST_API_KEY", "")

class IngestRecord(BaseModel):
    symbol: str
    label: str
    sec_type: str = "UNKNOWN"
    bid: float
    ask: float
    recorded_at: str = None  # pro ingest-bulk (historická data)

def _check_api_key(key: str):
    if key != INGEST_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

@app.post("/api/ingest")
def api_ingest(record: IngestRecord, x_api_key: str = Header(...)):
    _check_api_key(x_api_key)
    db.insert_spread(record.symbol, record.label, record.sec_type, record.bid, record.ask)
    return {"ok": True}

@app.post("/api/ingest-bulk")
def api_ingest_bulk(records: list[IngestRecord], x_api_key: str = Header(...)):
    """Migrace historických dat se zachováním původních timestampů."""
    _check_api_key(x_api_key)
    import psycopg2
    from datetime import datetime
    url = os.environ["DATABASE_URL"]
    ssl = "disable" if "railway.internal" in url else "require"
    conn = psycopg2.connect(url, sslmode=ssl)
    try:
        with conn.cursor() as cur:
            for r in records:
                spread = round(r.ask - r.bid, 6)
                ts = datetime.fromisoformat(r.recorded_at) if r.recorded_at else datetime.utcnow()
                cur.execute(
                    "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (r.symbol, r.label, r.sec_type, r.bid, r.ask, spread, ts),
                )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "count": len(records)}
```

### 3. Frontend polling (templates/index.html)

```javascript
// Refresh každých 60 sekund — bez reloadu stránky
async function refresh() {
    const res = await fetch('/api/averages-all');
    const data = await res.json();
    renderTable(data);
}
refresh();
setInterval(refresh, 60_000);
```

### 4. Collector (collector.py — minimální vzor)

```python
import httpx, os, time, logging
from dotenv import load_dotenv

load_dotenv()
REMOTE_URL = os.environ["REMOTE_INGEST_URL"]
API_KEY    = os.environ["REMOTE_API_KEY"]
INTERVAL   = 300  # sekund

def collect_one():
    # --- ZDE tvá logika sběru dat ---
    symbol = "EUR"
    bid, ask = get_data_from_source(symbol)
    # --------------------------------
    httpx.post(
        f"{REMOTE_URL}/api/ingest",
        json={"symbol": symbol, "label": "EUR/USD", "sec_type": "CASH", "bid": bid, "ask": ask},
        headers={"x-api-key": API_KEY},
        timeout=10
    )

while True:
    try:
        collect_one()
    except Exception as e:
        logging.error(f"Chyba sběru: {e}")
    time.sleep(INTERVAL)
```

### 5. Závislosti

**`requirements-web.txt`** (jen pro Railway):
```
fastapi
uvicorn[standard]
psycopg2-binary
jinja2
python-dotenv
httpx
```

**`nixpacks.toml`** (řekni Railway aby použil requirements-web.txt):
```toml
[phases.install]
cmds = ["pip install -r requirements-web.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**.env** (lokální, nikdy necommitovat):
```
REMOTE_INGEST_URL=https://xxx.up.railway.app
REMOTE_API_KEY=<vygeneruj: python -c "import secrets; print(secrets.token_hex(24))">
```

---

## Railway Setup — Konkrétní příkazy

### 1. Spoj projekt s Railway CLI

```bash
# Ověř přihlášení (token v ~/.railway/config.json)
railway whoami

# Nalinkuj projekt
railway link --project PROJECT_ID --environment ENV_ID --service SERVICE_ID
```

### 2. Vytvoř PostgreSQL service přes Railway UI

V Railway dashboardu: **New Service → Database → PostgreSQL**

Nastav proměnné:
- `POSTGRES_USER`: `postgres`
- `POSTGRES_PASSWORD`: `silne_heslo`
- `POSTGRES_DB`: `nazev_db`

### 3. Nastav DATABASE_URL na web service

**KRITICKÉ**: Reference `${{Postgres.DATABASE_URL}}` nefunguje pokud Postgres service nevystavuje tuto proměnnou. Nastav URL přímo:

```bash
railway variables --service web set \
  DATABASE_URL="postgresql://postgres:HESLO@postgres.railway.internal:5432/nazev_db"
```

Ověření:
```bash
railway variables --service web | grep DATABASE_URL
```

### 4. Nastav INGEST_API_KEY

```bash
railway variables --service web set \
  INGEST_API_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"
```

### 5. Deploy

```bash
railway up --detach
# Počkej ~60s, pak zkontroluj logy:
railway logs --service web | tail -20
```

---

## Migrace historických dat

Lokální SQLite je primární záloha. Po každém problému s Railway DB:

```python
import sqlite3, httpx

conn = sqlite3.connect('spreads.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT symbol,label,sec_type,bid,ask,recorded_at FROM spreads ORDER BY recorded_at").fetchall()
conn.close()

API_URL = "https://XXX.up.railway.app/api/ingest-bulk"
API_KEY = "tvuj_klic"
BATCH   = 200

for i in range(0, len(rows), BATCH):
    batch = [dict(r) for r in rows[i:i+BATCH]]
    r = httpx.post(API_URL, json=batch, headers={"x-api-key": API_KEY}, timeout=30)
    print(f"batch {i//BATCH+1}: {r.status_code} — {r.json()}")
```

---

## Záloha dat do gitu

Odstraň `data/` z `.gitignore`, exportuj lokální SQLite do CSV:

```python
import sqlite3, csv
conn = sqlite3.connect('spreads.db')
with open('data/spreads_backup.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['symbol','label','sec_type','bid','ask','spread','recorded_at'])
    for row in conn.execute("SELECT symbol,label,sec_type,bid,ask,spread,recorded_at FROM spreads ORDER BY recorded_at"):
        writer.writerow(row)
conn.close()
```

---

## Pasti a jejich řešení

| Problém | Příčina | Fix |
|---------|---------|-----|
| `${{Postgres.DATABASE_URL}}` je prázdné | Custom Postgres service nevystavuje DATABASE_URL | Nastav URL přímo: `railway variables --service web set DATABASE_URL="postgresql://..."` |
| `SSL required` na `railway.internal` | Interní Railway Postgres nepodporuje SSL | Detekuj URL: `ssl = "disable" if "railway.internal" in url else "require"` |
| `sslmode="require"` hardcoded ve více místech | Zapsáno v `main.py` i `database_pg.py` zvlášť | Vždy používej centrální `get_conn()` — nepřipojuj se k DB přímo z endpointů |
| Railway deploy nefunguje přes GitHub | Projekt nepoužívá GitHub auto-deploy, jen CLI | `railway up --detach` z lokálu |
| Dashboard zobrazuje 0 záznamů | App použila SQLite místo PostgreSQL | Zkontroluj `DATABASE_URL` → musí být nastavené na web service |
| `Python 3.9: X \| None` TypeError | Starší Python nepodporuje union type syntax | `from typing import Optional; Optional[X]` místo `X \| None` |
| Stará data zmizela po deployi | Nebyla v PostgreSQL, jen v SQLite | Spusť migraci přes `/api/ingest-bulk` (viz výše) |

---

## Checklist pro nový projekt

- [ ] Vytvoř `database.py` (SQLite) a `database_pg.py` (PostgreSQL)
- [ ] `main.py` auto-detekuje prostředí podle `DATABASE_URL`
- [ ] `/api/ingest` + `/api/ingest-bulk` s `x-api-key` auth
- [ ] Frontend: `setInterval(refresh, 60_000)` + `fetch('/api/averages-all')`
- [ ] `requirements-web.txt` + `nixpacks.toml` (bez lokálních závislostí)
- [ ] `.gitignore` obsahuje `.env` a `*.db`
- [ ] `data/` **není** v `.gitignore` (CSV zálohy)
- [ ] Railway: PostgreSQL service + nastavené `DATABASE_URL` + `INGEST_API_KEY`
- [ ] Lokální `.env`: `REMOTE_INGEST_URL` + `REMOTE_API_KEY`
- [ ] `collector.py` ukládá lokálně (SQLite) i odesílá na Railway
