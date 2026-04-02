---
name: fastapi-ingest-api
description: >
  FastAPI server s ingest endpointem pro příjem dat z externího collectoru.
  Obsahuje: API key auth, Pydantic validace, dual-DB auto-detekce (SQLite lokálně /
  PostgreSQL na Railway), bulk import historických dat, health check.

  Použij PROAKTIVNĚ kdykoliv projekt potřebuje:
  - server který přijímá data z lokálního skriptu
  - "ingest endpoint", "příjem dat z collectoru"
  - FastAPI + PostgreSQL + Railway
  - API key autentizaci pro POST endpointy
  - dual-DB (lokálně SQLite, produkce PostgreSQL)
  - "chci web kam posílám data"
---

# FastAPI Ingest API — Šablona

Základ pro každý projekt kde lokální skript posílá data na Railway server.

---

## Minimální funkční server (`main.py`)

```python
import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()

# --- Auto-detekce prostředí ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    import database_pg as db
else:
    import database as db

db.init_db()

# --- API key ---
INGEST_API_KEY = os.environ.get("INGEST_API_KEY", "")

def _check_api_key(key: str):
    """Zamítne požadavek pokud klíč nesedí. Prázdný klíč = auth vypnutá (lokální dev)."""
    if INGEST_API_KEY and key != INGEST_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

# --- Datový model ---
class IngestRecord(BaseModel):
    symbol: str
    label: str
    sec_type: str = "UNKNOWN"
    bid: float
    ask: float
    recorded_at: Optional[str] = None   # pro ingest-bulk (historická data)

# --- Endpointy ---

@app.get("/health")
def health():
    """Rychlý health check — Railway to volá při startu."""
    return {"ok": True, "db": "postgres" if DATABASE_URL else "sqlite"}

@app.post("/api/ingest")
def api_ingest(record: IngestRecord, x_api_key: str = Header(...)):
    """Příjem jednoho záznamu z collectoru."""
    _check_api_key(x_api_key)
    db.insert_spread(record.symbol, record.label, record.sec_type, record.bid, record.ask)
    return {"ok": True}

@app.post("/api/ingest-bulk")
def api_ingest_bulk(records: list[IngestRecord], x_api_key: str = Header(...)):
    """
    Migrace historických dat se zachováním původních timestampů.
    Používá přímé psycopg2 spojení aby mohl nastavit recorded_at.
    """
    _check_api_key(x_api_key)

    if not DATABASE_URL:
        # Lokálně — ulož do SQLite bez recorded_at override
        for r in records:
            db.insert_spread(r.symbol, r.label, r.sec_type, r.bid, r.ask)
        return {"ok": True, "count": len(records)}

    import psycopg2
    ssl = "disable" if "railway.internal" in DATABASE_URL else "require"
    conn = psycopg2.connect(DATABASE_URL, sslmode=ssl)
    try:
        with conn.cursor() as cur:
            for r in records:
                spread = round(r.ask - r.bid, 6)
                ts = datetime.fromisoformat(r.recorded_at) if r.recorded_at else datetime.utcnow()
                cur.execute(
                    "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (r.symbol, r.label, r.sec_type, r.bid, r.ask, spread, ts),
                )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "count": len(records)}

@app.get("/api/averages-all")
def api_averages_all():
    """Průměry za všechna data — volá frontend polling."""
    return db.get_averages()

@app.get("/")
def index():
    """HTML dashboard."""
    return HTMLResponse(content=open("templates/index.html").read())
```

---

## Databázová vrstva

### `database.py` — SQLite (lokálně)

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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT NOT NULL,
            label       TEXT NOT NULL,
            sec_type    TEXT NOT NULL DEFAULT 'UNKNOWN',
            bid         REAL,
            ask         REAL,
            spread      REAL,
            recorded_at TEXT NOT NULL
        )""")

def insert_spread(symbol, label, sec_type, bid, ask):
    spread = round(ask - bid, 6) if bid and ask else None
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) VALUES (?,?,?,?,?,?,?)",
            (symbol, label, sec_type, bid, ask, spread, datetime.utcnow().isoformat())
        )

def get_averages():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT symbol, label, sec_type,
                   AVG(spread) as avg_spread,
                   MIN(spread) as min_spread,
                   MAX(spread) as max_spread,
                   COUNT(*)    as samples
            FROM spreads
            WHERE spread IS NOT NULL
            GROUP BY symbol, label, sec_type
            ORDER BY label
        """).fetchall()
    return [dict(r) for r in rows]
```

### `database_pg.py` — PostgreSQL (Railway)

```python
import os, psycopg2, psycopg2.extras
from datetime import datetime

def get_conn():
    url = os.environ["DATABASE_URL"]
    ssl = "disable" if "railway.internal" in url else "require"
    conn = psycopg2.connect(url, sslmode=ssl)
    conn.autocommit = False
    return conn

def init_db():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS spreads (
                id          SERIAL PRIMARY KEY,
                symbol      TEXT NOT NULL,
                label       TEXT NOT NULL,
                sec_type    TEXT NOT NULL DEFAULT 'UNKNOWN',
                bid         REAL,
                ask         REAL,
                spread      REAL,
                recorded_at TIMESTAMP NOT NULL
            )""")
        conn.commit()
    finally:
        conn.close()

def insert_spread(symbol, label, sec_type, bid, ask, recorded_at=None):
    spread = round(ask - bid, 6) if bid and ask else None
    ts = recorded_at or datetime.utcnow()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO spreads (symbol,label,sec_type,bid,ask,spread,recorded_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (symbol, label, sec_type, bid, ask, spread, ts)
            )
        conn.commit()
    finally:
        conn.close()

def get_averages():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT symbol, label, sec_type,
                       AVG(spread) as avg_spread,
                       MIN(spread) as min_spread,
                       MAX(spread) as max_spread,
                       COUNT(*)    as samples
                FROM spreads
                WHERE spread IS NOT NULL
                GROUP BY symbol, label, sec_type
                ORDER BY label
            """)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
```

---

## Závislosti (`requirements-web.txt`)

```
fastapi
uvicorn[standard]
psycopg2-binary
jinja2
python-dotenv
httpx
```

## Railway build (`nixpacks.toml`)

```toml
[phases.install]
cmds = ["pip install -r requirements-web.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

---

## Generování API klíče

```bash
# Vygeneruj nový klíč
python3 -c "import secrets; print(secrets.token_hex(24))"

# Nastav na Railway
railway variables --service web set INGEST_API_KEY="<vygenerovaný klíč>"

# Ulož do lokálního .env
echo "REMOTE_API_KEY=<klíč>" >> .env
```

---

## Testování endpointů

```bash
# Health check
curl https://xxx.up.railway.app/health

# Odeslání jednoho záznamu
curl -X POST https://xxx.up.railway.app/api/ingest \
  -H "Content-Type: application/json" \
  -H "x-api-key: tvuj_klic" \
  -d '{"symbol":"EUR","label":"EUR/USD","sec_type":"CASH","bid":1.0800,"ask":1.0801}'

# Ověření dat
curl https://xxx.up.railway.app/api/averages-all | python3 -m json.tool
```

---

## Časté chyby

| Chyba | Příčina | Fix |
|-------|---------|-----|
| `422 Unprocessable Entity` | Pydantic odmítl data — chybí povinné pole nebo špatný typ | Zkontroluj JSON strukturu, všechna required pole (`symbol`, `label`, `bid`, `ask`) |
| `403 Forbidden` | Špatný nebo chybějící `x-api-key` header | Ověř že header je `x-api-key` (ne `Authorization`) a klíč sedí |
| `500` na ingest-bulk | SSL chyba nebo chybí `recorded_at` format | Viz skill `db-migrate` |
| `list[IngestRecord]` — Python 3.9 | `list[X]` jako typ není v Python 3.9 podporováno v runtime | Použij `from typing import List` a `List[IngestRecord]` |
| App nestartuje | Chyba v importu nebo init_db() | `railway logs --service web | head -30` |
