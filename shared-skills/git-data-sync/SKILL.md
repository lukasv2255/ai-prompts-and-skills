---
name: git-data-sync
description: >
  Verzování datových exportů v gitu pro synchronizaci mezi více počítači.
  Export SQLite/DB do CSV, naming convention, merge strategie, migrace
  sloučených dat na Railway.

  Použij PROAKTIVNĚ kdykoliv zazní:
  - "data na druhém počítači", "synchronizuj data"
  - "data nejsou na Gitu", "záloha dat do gitu"
  - "sbírám na dvou strojích", "slouč data"
  - "přenes data na nový počítač"
  - "git sync data", "CSV export"
---

# Git Data Sync — synchronizace dat přes git

Odzkoušeno na spread-monitor: Mac mini sbírá data → exportuje do `data/spreads_mac-mini.csv` → push → na druhém stroji pull → merge → migrace na Railway.

---

## Základní princip

```
Stroj A (mac-mini)               Stroj B (macbook)
spreads.db                       spreads.db
    ↓ export                         ↓ export
data/spreads_mac-mini.csv        data/spreads_macbook.csv
    ↓ git push                       ↓ git push
                  GitHub repo
                      ↓ Railway migrace
              PostgreSQL (všechna data)
```

---

## 1. Nastavení `.gitignore`

```bash
# *.db NESMÍ být v gitu (velké, binární, mění se každou sekundu)
# data/ MUSÍ být v gitu (CSV zálohy)

# Ověř .gitignore
grep -n "data" .gitignore
```

Pokud `data/` je v `.gitignore`, odstraň řádek:
```bash
# Uprav .gitignore — odstraň řádek "data/"
# Nebo okomentuj:
# data/   ← toto odstraň nebo okomentuj
```

---

## 2. Export lokální SQLite do CSV

```python
# export_data.py — spusť na každém stroji před push
import sqlite3, csv, platform
from pathlib import Path
from datetime import datetime

# Název souboru podle stroje — aby nedocházelo ke konfliktům
MACHINE = platform.node().split('.')[0].lower()   # např. "mac-mini", "macbook"
OUT_FILE = Path(f"data/spreads_{MACHINE}.csv")
Out_FILE.parent.mkdir(exist_ok=True)

conn = sqlite3.connect("spreads.db")
rows = conn.execute(
    "SELECT symbol, label, sec_type, bid, ask, spread, recorded_at "
    "FROM spreads ORDER BY recorded_at ASC"
).fetchall()
conn.close()

with open(OUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["symbol", "label", "sec_type", "bid", "ask", "spread", "recorded_at"])
    writer.writerows(rows)

print(f"Exportováno {len(rows)} záznamů → {OUT_FILE}")
```

```bash
python3 export_data.py
git add data/
git commit -m "Export dat z $(hostname) — $(date +%Y-%m-%d)"
git push
```

---

## 3. Merge dat z více strojů → Railway

Po pull na libovolném stroji (nebo přímo z gitu) slouč všechny CSV:

```python
# merge_and_migrate.py
import csv, httpx, glob
from pathlib import Path

API_URL = "https://xxx.up.railway.app/api/ingest-bulk"
API_KEY = "tvuj_klic"
BATCH   = 200

# Načti všechny CSV soubory z data/
all_rows = []
seen     = set()   # deduplication: (symbol, recorded_at)

for csv_file in sorted(Path("data").glob("spreads_*.csv")):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["symbol"], row["recorded_at"])
            if key not in seen:
                seen.add(key)
                all_rows.append(row)
    print(f"  {csv_file.name}: {sum(1 for r in open(csv_file))- 1} řádků")

# Seřaď chronologicky
all_rows.sort(key=lambda r: r["recorded_at"])
print(f"Celkem unikátních záznamů: {len(all_rows)}")

# Odešli na Railway
total = 0
for i in range(0, len(all_rows), BATCH):
    batch = all_rows[i:i+BATCH]
    # Přidej float konverzi (CSV je string)
    payload = []
    for r in batch:
        try:
            payload.append({
                "symbol":      r["symbol"],
                "label":       r["label"],
                "sec_type":    r.get("sec_type", "UNKNOWN"),
                "bid":         float(r["bid"]) if r["bid"] else 0,
                "ask":         float(r["ask"]) if r["ask"] else 0,
                "recorded_at": r["recorded_at"],
            })
        except (ValueError, KeyError):
            continue  # přeskoč poškozený řádek

    r = httpx.post(API_URL, json=payload, headers={"x-api-key": API_KEY}, timeout=30)
    if r.status_code == 200:
        total += r.json()["count"]
        print(f"  batch {i//BATCH + 1}: OK — {total}/{len(all_rows)}")
    else:
        print(f"  CHYBA: {r.status_code} {r.text[:200]}")
        break

print(f"Migrace hotova: {total} záznamů")
```

---

## 4. Workflow pro nový projekt

**Při každém sběru dat (volitelně — nebo jen jednou za den):**
```bash
python3 export_data.py && git add data/ && git commit -m "data update" && git push
```

**Při spojení dat z více strojů:**
```bash
git pull                     # stáhni CSV ze všech strojů
python3 merge_and_migrate.py # slouč a pošli na Railway
```

---

## Naming convention pro CSV soubory

```
data/
├── spreads_mac-mini.csv      ← stroj "mac-mini"
├── spreads_macbook-pro.csv   ← stroj "macbook-pro"
└── spreads_backup.csv        ← manuální záloha (libovolný stroj)
```

**Proč `platform.node()`:** vrátí hostname stroje → unikátní název souboru → žádné git konflikty při push z různých strojů na stejnou větev.

---

## Git konflikty při merge CSV

Pokud dva stroje editují **stejný soubor** (špatný naming), vznikne git conflict. Proto:
- Každý stroj má **vlastní soubor** (`spreads_mac-mini.csv` vs `spreads_macbook.csv`)
- `merge_and_migrate.py` deduplication řeší překryvy v datech

---

## Kdy NEUKLÁDAT data do gitu

- Data jsou > 50 MB → použij LFS nebo jen migruj přes API bez zálohy v gitu
- Data se mění každou sekundu → commit jen jednou denně/týdně
- Citlivá data (osobní údaje, tokeny) → nikdy do gitu

---

## Alternativa: export při každém git push (git hook)

```bash
# .git/hooks/pre-push
#!/bin/bash
python3 export_data.py
git add data/
git commit --amend --no-edit   # připoj export k poslednímu commitu
```

```bash
chmod +x .git/hooks/pre-push
```

**Pozor:** `--amend` přepisuje commit — nepoužívej na shared branch kde jiní pushují.
