---
name: railway-parity
description: >
  Audit a sjednocení chování lokálního běhu vs Railway deploye pro LIBOVOLNÝ
  projekt. Detekuje rozdíly v env proměnných, persistenci (volume vs efemerní FS),
  polling/scheduler intervalech, port bindingu, file paths a stavových souborech.
  Cílem je PARITY — Railway se chová stejně jako localhost.

  Použij PROAKTIVNĚ kdykoliv zazní:
  - "chci to rozběhnout na Railway stejně jako lokálně"
  - "Railway se chová jinak než localhost"
  - "logy / data / stavy se nepřenesly na Railway"
  - "polling / scheduler na Railway je pomalejší"
  - "po deploy se ztratily logy / cache / DB"
  - "agent / worker nezpracuje úkol" / "stav nezmizí" / "queue prázdná"
  - "co je jiné na Railway", "Railway parity audit"
---

# Railway ↔ Localhost Parity Audit

Když aplikace běží lokálně jinak než na Railway, jde **skoro vždy o jednu ze 4 příčin**:

1. **Env vars** — jiné hodnoty (interval, flagy, paths, secrets)
2. **Persistence** — kód píše do efemerního FS místo volume
3. **Polling / scheduler** — pomalejší cyklus, baseline-skip mechanismy
4. **Stavový drift** — Railway nezná lokální historii (cursory, ledgery, cache)

Tento skill je checklist + diagnostické příkazy. V ~5 minutách zjistíš, který z těch
čtyř to je. Funguje pro libovolný stack (Python, Node, Go, …) — pravidla závisí na
chování Railway, ne na frameworku.

**Klíčové pravidlo:** nepřepisuj nic na Railway, dokud nemáš diff zmapovaný a uživatel
neodsouhlasil. Zápis na volume / restart služby je viditelná akce.

---

## Krok 1 — Diff env proměnných

```bash
cd <project>

# Railway env (přes railway run, do souboru pro porovnání)
railway run -- bash -lc 'env' \
  | grep -vE "^(PATH|HOME|PWD|SHLVL|_|LANG|LC_|TERM|HOSTNAME|USER|SHELL|TMPDIR|OLDPWD|XPC_|__CF|SSH_)" \
  | sort > /tmp/railway_env.txt

# Lokální env (z .env nebo aktuálního shellu)
( set -a; source .env 2>/dev/null; set +a; env ) \
  | grep -vE "^(PATH|HOME|PWD|SHLVL|_|LANG|LC_|TERM|HOSTNAME|USER|SHELL|TMPDIR|OLDPWD|XPC_|__CF|SSH_)" \
  | sort > /tmp/local_env.txt

# Co je jen lokálně / jen na Railway / kde se hodnoty liší
echo "=== ONLY ON LOCAL ==="
comm -23 <(cut -d= -f1 /tmp/local_env.txt | sort -u) \
         <(cut -d= -f1 /tmp/railway_env.txt | sort -u)
echo "=== ONLY ON RAILWAY ==="
comm -13 <(cut -d= -f1 /tmp/local_env.txt | sort -u) \
         <(cut -d= -f1 /tmp/railway_env.txt | sort -u)
echo "=== DIFFERENT VALUES ==="
for k in $(comm -12 <(cut -d= -f1 /tmp/local_env.txt | sort -u) \
                    <(cut -d= -f1 /tmp/railway_env.txt | sort -u)); do
  L=$(grep "^$k=" /tmp/local_env.txt | head -1)
  R=$(grep "^$k=" /tmp/railway_env.txt | head -1)
  [ "$L" != "$R" ] && echo "L: $L" && echo "R: $R" && echo
done
```

**Co kontrolovat (sklony které vznikají v každém projektu):**

| Kategorie           | Typické názvy                                                 | Proč to bývá rozdílné                                                 |
| ------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------- |
| Polling / scheduler | `*_INTERVAL*`, `*_POLL*`, `CHECK_*`, `CRON_*`                 | Lokálně rychlý cyklus pro dev feedback, na Railway pomalý kvůli quotě |
| Feature flagy       | `AUTO_*`, `DRY_RUN`, `*_ENABLED`, `MODULE_*`, `FEATURE_*`     | Produkce dělá víc/míň věcí než dev                                    |
| Paths               | `DATA_DIR`, `LOG_DIR`, `CACHE_DIR`, `STATE_DIR`, `UPLOAD_DIR` | Lokálně `./data`, Railway musí mířit na `/data` (volume)              |
| Auth / OAuth        | `*_REDIRECT_URI`, `*_CALLBACK_URL`, `OAUTH_*`                 | Lokálně `http://localhost:<port>`, Railway public doména              |
| DB / API URL        | `DATABASE_URL`, `*_API_URL`, `*_HOST`                         | Lokální mock vs production backend                                    |
| Šifrovací klíče     | `VAULT_KEY`, `FERNET_KEY`, `SECRET_KEY`, `JWT_SECRET`         | Musí se SHODOVAT, jinak nedešifruješ stávající data (viz krok 2)      |
| Railway internals   | `RAILWAY_*`, `PORT`                                           | Railway je injectuje sám — **ignoruj** rozdíl                         |

**Pozor:** Railway `RAILWAY_VOLUME_MOUNT_PATH` injectuje do shellu, ale **kód musí
ten path explicitně číst** (`os.getenv(...)`, `process.env...`). Default `./data`
v kódu vede do efemerního FS, i když volume existuje.

---

## Krok 2 — Volume / persistence audit

```bash
# Které volumes jsou připojené a kam
railway volume list

# Skutečný obsah volume
railway ssh "ls -la /data/ 2>&1; echo '---'; du -sh /data/* 2>/dev/null"

# Mapování env → kód: kde se path proměnné v kódu používají
# (uprav vzory podle stacku — DATA_DIR, LOG_DIR, CACHE_DIR, STATE_DIR…)
grep -rnE "DATA_DIR|LOG_DIR|CACHE_DIR|STATE_DIR|RAILWAY_VOLUME" \
  --include='*.py' --include='*.js' --include='*.ts' --include='*.go' \
  --include='*.rs' --include='*.rb' --include='*.java' \
  src/ lib/ app/ *.py *.js *.ts 2>/dev/null
```

**Tři pasti, které potkáš v každém projektu:**

1. **Volume existuje, ale kód píše jinam.** Relativní cesta (`./data`) místo
   `os.getenv("DATA_DIR")` znamená, že volume je sice mountnutý, ale aplikace ho
   nepoužívá. Test: zapiš testovací soubor přes app a hledej ho přes
   `railway ssh "find / -name <jméno> 2>/dev/null"`.

2. **Logy v efemerním FS.** `DATA_DIR` setnutý na `/data`, ale `LOG_DIR` zůstal
   default `./logs` → log soubory přežijí jen do dalšího deploy. Fix: `LOG_DIR`
   musí mířit na volume (typicky `/data/logs/agent`).

3. **Šifrované soubory bez ověření klíče.** Soubory chráněné symetrickým klíčem
   (`*.enc`, vaults, sealed secrets, age, Fernet) nelze přepsat lokální verzí,
   pokud klíč na Railway neodpovídá klíči, kterým byly zašifrovány lokálně.
   Test:
   ```bash
   railway run -- bash -lc 'echo -n "$VAULT_KEY" | shasum -a 256 | cut -c1-16'
   echo -n "$(grep ^VAULT_KEY= .env | cut -d= -f2-)" | shasum -a 256 | cut -c1-16
   ```
   Hash se shoduje → bezpečně přepiš. Neshoduje → **NEPŘEPISUJ** (přijdeš o data).
   Stejný postup pro libovolný klíč (`FERNET_KEY`, `SECRET_KEY`, `MASTER_KEY` …).

---

## Krok 3 — Polling / scheduler / cron parity

Pokud aplikace cyklicky kontroluje něco (IMAP/queue/API/DB/scraper/cron job):

- Lokál typicky **krátký interval** (1–10 s pro dev feedback)
- Railway často **dlouhý interval** (30–60 min kvůli quota / nákladům)

→ Pokud uživatel chce paritu, sjednoť hodnoty:

```bash
railway variables --set CHECK_INTERVAL_MINUTES=1
# nebo --set POLL_INTERVAL_SECONDS=5, --set CRON_SCHEDULE="* * * * *", …
```

**Druhotný efekt pomalého pollingu — baseline / cursor pasti:**

Mnoho služeb má při startu **"skip backlog" mechanismus**: ignoruje záznamy ≤
aktuální max ID, aby se po deploy nezahltily starou frontou. Lokálně s rychlým
pollingem je to neviditelné (cursor se posouvá pořád), Railway s pomalým
intervalem = nový záznam visí celý interval.

Hledej v kódu tyto vzory:

- `baseline`, `cursor`, `last_seen_*`, `since_id`, `last_processed_*`
- `SKIP_BACKLOG`, `SKIP_OLD`, `PROCESS_HISTORY=false`
- `startup_baseline`, `prime_cursor`, `seek_to_end`

Pokud uživatel restartoval službu a očekává, že dobere staré záznamy, **musíš
cursor resetovat** (na hodnotu před nejstarším nepřebíraným záznamem), ne čekat
na další poll.

---

## Krok 4 — Stavový sync (lokál → Railway)

Pokud lokál něco zpracoval a Railway o tom neví (prázdná historie, UI ukazuje
"čeká na zpracování", duplicitní zpracování), je to **state drift**.

**Identifikuj stavové soubory** — nezávisle na frameworku spadají do těchto kategorií:

| Typ                | Typická koncovka / názvy                                | Co obsahuje                           |
| ------------------ | ------------------------------------------------------- | ------------------------------------- |
| Append-only log    | `*.jsonl`, `*.log`, `*.ndjson`, `events.*`              | Co aplikace už zpracovala (ledger)    |
| Embedded DB        | `*.db`, `*.sqlite*`, `*.duckdb`                         | Persistovaná data, cache, fronta      |
| Cursor / pointer   | `*_cursor.json`, `state.json`, `last_*.json`            | Kde aplikace skončila                 |
| Cache              | `manual_replies.json`, `cache.json`, `*.pkl`, `*.cache` | Dohledaná data, drahá na regenerování |
| Sealed credentials | `*.enc`, `vault.*`, `*.sealed`                          | Šifrované secrets (pozor na krok 2!)  |

**Bezpečný sync pattern:**

```bash
# 1) Záloha současného stavu Railway volume — VŽDY před přepisem
railway ssh "tar -czf /data/.backup_$(date +%Y%m%d_%H%M%S).tgz \
            --exclude='*.tgz' --exclude='lost+found' -C /data ."

# 2) Přenos lokálních souborů → Railway
#    Stdin přes `railway ssh` NEFUNGUJE (vznikne 0 B soubor) — viz pasti níže.
#    Pro malé soubory (≤ ~130 KB) použij base64 inline.
#    Pro větší rozděl na chunky, pošli jeden po druhém:

tar -czf /tmp/state.tgz -C data <jen-state-soubory>
base64 -i /tmp/state.tgz | tr -d '\n' > /tmp/state.b64
split -a 4 -b 130000 /tmp/state.b64 /tmp/chunk_

# První chunk overwrite, ostatní append
FIRST=1
for f in /tmp/chunk_*; do
  CHUNK=$(cat "$f")
  if [ $FIRST -eq 1 ]; then
    railway ssh "echo -n '$CHUNK' > /data/_upload.b64"
    FIRST=0
  else
    railway ssh "echo -n '$CHUNK' >> /data/_upload.b64"
  fi
done

# 3) Dekódovat a ověřit SHA256
LOCAL_SHA=$(shasum -a 256 /tmp/state.tgz | cut -d' ' -f1)
railway ssh "base64 -d /data/_upload.b64 > /data/_upload.tgz && \
            sha256sum /data/_upload.tgz | cut -d' ' -f1"
# musí se shodovat s LOCAL_SHA

# 4) Rozbalit do správných cílů
railway ssh "mkdir -p /data/_staging && \
             tar -xzf /data/_upload.tgz -C /data/_staging && \
             mv /data/_staging/<file> /data/<target>/<file> && \
             chown root:root /data/<target>/<file> && \
             rm -rf /data/_staging /data/_upload.*"
```

**Co skipnout při přenosu:**

- `.DS_Store`, `Thumbs.db`, `__pycache__/`, `.pytest_cache/`, `node_modules/`
- QA / test artefakty (typicky `test_runs/`, `qa/`, `judge_runs/`, `fixtures/`)
- Lokální mock data, pokud produkce má vlastní zdroj pravdy
- Logy starší než pár dnů (nafukují volume)

---

## Krok 5 — Restart a verifikace

```bash
# Restart (Railway si pamatuje config, jen znovu spustí kontejner)
railway redeploy   # force nový deploy
# nebo: railway service restart   (kde podporováno)

# Sleduj logy startupu
railway logs --deployment 2>&1 | tail -40
```

**Co ověřit v logu:**

- ✓ Startup parametry odpovídají lokálním (interval, moduly, paths, feature flagy)
- ✓ Stavové soubory se načetly bez chyb
- ✓ Listener / scheduler / worker naběhl
- ✗ Žádné `FileNotFoundError`, `PermissionError`, `EACCES` na volume
- ✗ Žádné `Failed to decrypt` / `Invalid token` (= klíč mismatch z kroku 2)

Pak otevři aplikaci (dashboard URL, API endpoint, …) a **manuálně ověř scénář,
který byl rozbitý**. Logy můžou hlásit "vše OK" a UI přesto ukazovat starý stav
kvůli front-end cachím.

---

## Bezpečnostní pravidla skillu

1. **Nikdy neprováděj `railway up` ani `railway redeploy` automaticky.** Vždy
   připrav příkaz a počkej na explicitní "go" od uživatele.
2. **Před přepisem volume udělej tar zálohu na samotném volume**
   (`/data/.backup_<datum>.tgz`) — i kdyby tam skoro nic nebylo.
3. **Šifrované soubory přepisuj jen po ověření shody klíče.** Bez toho přijdeš
   o data nevratně.
4. **Nemaž efemerní logy ručně** — projdou samy po dalším deploy.
5. **Necommituj data dump do gitu** jako transit — i když to "rychle vyřeší".
   Skončí to v historii navždy a v public reposu jako data leak.

---

## Známé pasti `railway ssh` / CLI

- **Stdin redirect přes `railway ssh` NEFUNGUJE.** `echo X | railway ssh "cat > /file"`
  vytvoří soubor 0 B. Použij base64 v argumentu (limit ~130 KB / příkaz kvůli
  `Argument list too long`) nebo rozsekej na chunky a posílej jeden po druhém.
- **Žádné `curl`/`wget`/`scp` v default kontejnerech.** Některé Railway images
  obsahují jen interpret (`python3`, `node`) — `urllib`/`http` modul jediná cesta
  pro HTTP transfer.
- **`railway variables --set` triggeruje deploy.** Pokud nechceš restart, použij
  `--skip-deploys`, env se uplatní až při příštím (manuálním) deploy.
- **`railway run` na lokále** spustí příkaz s Railway env injectovaným do
  **lokálního shellu** — dobré pro diff env, ale **neběží to v Railway kontejneru**.
  Pro běh v kontejneru použij `railway ssh`.

---

## Quick checklist (kopíruj do PR / issue / task description)

```
[ ] railway variables diff proti .env projetý, rozdíly schváleny
[ ] DATA_DIR / LOG_DIR / další path env ukazují na volume mount (/data)
[ ] Šifrovací klíče (VAULT_KEY, FERNET_KEY, SECRET_KEY …) se shodují (SHA test)
[ ] Polling / cron interval = lokální hodnota (nebo vědomý rozdíl)
[ ] Feature flagy (AUTO_*, DRY_RUN, MODULE_*, *_ENABLED) sjednoceny
[ ] Backup Railway volume vytvořen (/data/.backup_YYYYMMDD.tgz)
[ ] Stavové soubory přeneseny (*.jsonl, *.db, *.json, cursors)
[ ] SHA256 integrity check po přenosu prošel
[ ] Restart proveden, startup log čistý (žádné FileNotFound / Permission errors)
[ ] Konkrétní rozbitý scénář manuálně ověřen v UI / API
[ ] Citlivé soubory NEpřenesené přes git ani 3rd party (nebo explicitně schváleno)
```

---

## Kdy tento skill NEpoužívat

- Když uživatel jen chce **prostý deploy nového kódu** — to je `railway-deploy`
  nebo `railway-redeploy` skill.
- Když má app **úplně jiný runtime** než lokál (Lambda, Cloud Run, K8s) — Railway
  parity je jen pro Railway containers.
- Když rozdíl je **vědomě navržený** (např. produkční DB má jiná data než dev
  fixture) — sjednocení by porušilo separaci prostředí.
