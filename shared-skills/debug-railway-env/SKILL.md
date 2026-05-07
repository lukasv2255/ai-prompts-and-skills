---
name: debug-railway-env
description: >
  Systematické ladění env proměnných na Railway — proč jsou prázdné,
  jak je správně nastavit, jak ověřit že se skutečně načítají v běžící app.

  Použij PROAKTIVNĚ kdykoliv zazní:
  - "DATABASE_URL je prázdné / nefunguje"
  - "app na Railway nevidí proměnnou"
  - "reference variable nefunguje"
  - "${{Postgres.DATABASE_URL}} je prázdné"
  - "env var na Railway", "Railway proměnné"
  - "app crashuje po deployi", "0 záznamů v DB"
  - "proměnná je nastavená ale app ji nevidí"
---

# Debug Railway Environment Variables

Odzkoušeno na spread-monitor: `${{Postgres.DATABASE_URL}}` reference byla prázdná hodinu než jsme zjistili proč.

---

## Rychlá diagnóza (začni tady)

```bash
# 1. Zobraz aktuální proměnné web service
railway variables --service web

# 2. Zobraz proměnné Postgres service
railway variables --service Postgres

# 3. Zkontroluj logy — co app říká při startu
railway logs --service web | tail -30
```

**Co hledáš v logu:**
- `DATABASE_URL` je prázdné → app padá na SQLite nebo crashuje
- `sslmode="require"` + `railway.internal` → SSL error → app crashuje
- `ModuleNotFoundError` → chybí balíček v `requirements-web.txt`

---

## Problém 1: `${{Postgres.DATABASE_URL}}` je prázdné

### Příčina
Railway reference proměnné `${{ServiceName.VAR}}` fungují **pouze pokud zdrojová service tuto proměnnou exportuje**. Custom PostgreSQL service (Docker container) ji nevystavuje automaticky — vystavuje jen `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.

### Rychlé ověření
```bash
railway variables --service Postgres
# Vidíš DATABASE_URL? Pokud ne → reference nefunguje
```

### Fix: nastav DATABASE_URL přímo
```bash
railway variables --service web set \
  DATABASE_URL="postgresql://postgres:HESLO@postgres.railway.internal:5432/DBNAME"
```

Kde hodnoty najdeš:
- `HESLO` → `railway variables --service Postgres | grep PASSWORD`
- `DBNAME` → `railway variables --service Postgres | grep DB`
- Hostname je vždy `postgres.railway.internal` pro interní komunikaci

### Ověření po nastavení
```bash
railway variables --service web | grep DATABASE_URL
# Musíš vidět celou URL, ne prázdný řetězec
```

---

## Problém 2: Proměnná je nastavená ale app ji nevidí

### Příčina
App byla nasazena **před** nastavením proměnné. Env vars se načítají při startu kontejneru, ne za běhu.

### Fix
```bash
# Redeploy aby se načetly nové proměnné
railway up --detach
sleep 60
railway logs --service web | tail -10
```

### Ověření zevnitř app
```bash
railway run --service web python3 -c "import os; print('DB=', os.environ.get('DATABASE_URL', 'PRÁZDNÉ')[:50])"
```

---

## Problém 3: Reference variable funguje v UI ale ne přes API

### Příčina
Nastavení přes GraphQL API (`variableUpsert`) uloží **literální string** `${{Postgres.DATABASE_URL}}` — Railway ho nerozloží na skutečnou hodnotu. Reference fungují **pouze přes Railway UI**.

### Fix
Nepoužívej reference — nastav vždy konkrétní hodnotu přes CLI:
```bash
railway variables --service web set DATABASE_URL="postgresql://..."
```

---

## Problém 4: App používá SQLite místo PostgreSQL

### Příčina
`main.py` volí DB podle `os.environ.get("DATABASE_URL")` — pokud je prázdné, použije SQLite. Na Railway je SQLite ephemeral (smaže se při deployi) → dashboard zobrazuje 0 záznamů.

### Diagnóza
```bash
# Zkontroluj API — vrací data?
curl -s https://xxx.up.railway.app/api/averages-all | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'{len(d)} symbolů, {sum(x[\"samples\"] for x in d)} záznamů')
"
```

Pokud `0 záznamů` → app je na SQLite → DATABASE_URL je prázdné.

### Fix
1. Nastav `DATABASE_URL` (viz Problém 1)
2. Redeploy
3. Spusť migraci dat (viz skill `db-migrate`)

---

## Problém 5: SSL error po nastavení DATABASE_URL

### Příčina
`postgres.railway.internal` nepodporuje SSL. Pokud kód má `sslmode="require"` hardcoded, app crashuje.

### Příznaky v logu
```
psycopg2.OperationalError: server does not support SSL, but SSL was required
```

### Fix v kódu
```python
# database_pg.py a VŠECHNA místa kde se připojuješ k DB
url = os.environ["DATABASE_URL"]
ssl = "disable" if "railway.internal" in url else "require"
conn = psycopg2.connect(url, sslmode=ssl)
```

**Pozor:** Zkontroluj `main.py` — pokud má endpoint `/api/ingest-bulk` vlastní `psycopg2.connect`, musíš opravit i tam. Centralizuj vždy do `get_conn()`.

---

## Kompletní checklist při "app nefunguje na Railway"

```
□ railway variables --service web      → DATABASE_URL nastavené?
□ railway variables --service Postgres → POSTGRES_USER/PASSWORD/DB nastavené?
□ railway logs --service web           → SSL error? ModuleNotFound? Jiná chyba?
□ curl /api/averages-all               → vrací data nebo prázdné pole?
□ railway run --service web python3 -c "import os; print(os.environ.get('DATABASE_URL','')[:60])"
                                       → DATABASE_URL je skutečně nastavené v runtime?
□ Po každé změně proměnné → railway up --detach (nebo restart service v UI)
```

---

## IDs spread-monitor (pro referenci)

| Klíč | Hodnota |
|------|---------|
| Project ID | viz Railway dashboard |
| Environment ID | viz Railway dashboard |
| Web service ID | viz Railway dashboard |
| Postgres service ID | viz Railway dashboard |
| Token | viz railway.app/account/tokens |
| DATABASE_URL (interní) | viz Railway → Postgres → Variables |
