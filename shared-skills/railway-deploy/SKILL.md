---
name: railway-deploy
description: Nasaď projekt na Railway, nastav env proměnné, zkontroluj logy. Použij když uživatel říká "nasaď na Railway", "deploy", "zkontroluj Railway logy", nebo "nastav env vars".
allowed-tools: Bash, Read, Glob
---

# Railway Deploy

## Prerekvizity

Railway token a project/service IDs jsou v `docs/project_notes/key_facts.md` nebo `CLAUDE.md`.

## 1. Získání Railway API tokenu (nutné jednou)

**Uživatel musí manuálně:**
1. Jít na railway.app/account/tokens
2. Kliknout **Create Token** → pojmenovat "project-name"
3. Zkopírovat token a poslat do chatu

**Railway CLI neakceptuje RAILWAY_TOKEN přes bash env var na Windows.**
Místo toho zapiš token přímo do konfiguračního souboru CLI:

```python
import json, os
config_dir = 'C:/Users/tommy/.railway'  # ~/.railway — NIKOLI AppData/Roaming
os.makedirs(config_dir, exist_ok=True)
config = {'projects': {}, 'user': {'token': 'TOKEN_ZDE'}}
with open(f'{config_dir}/config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

Ověření: `C:/Users/tommy/railway.exe whoami` → musí vrátit email.

> **Proč AppData nefunguje:** Railway CLI v4 (Rust) používá `dirs::home_dir()` → `~/.railway/config.json`.
> AppData/Roaming je jiná cesta. `RAILWAY_TOKEN` env var nefunguje spolehlivě na Windows přes bash.

## 2. Instalace Railway CLI (pokud chybí)

```bash
# Stáhni správnou verzi z GitHub releases API
curl -s "https://api.github.com/repos/railwayapp/cli/releases/latest" | python -c "
import sys, json
data = json.load(sys.stdin)
assets = data['assets']
url = next(a['browser_download_url'] for a in assets if 'x86_64-pc-windows-msvc.zip' in a['name'])
print(url)
"
# Stáhni zip, rozbal, zkopíruj railway.exe do C:/Users/tommy/railway.exe
```

## 3. Vytvoření projektu a nasazení

### Workspace ID (potřebné pro vytvoření projektu)
```bash
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ me { id workspaces { id name } } }"}'
```

### Vytvoření projektu
```bash
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { projectCreate(input: {name: \"NAME\", workspaceId: \"WORKSPACE_ID\"}) { id environments { edges { node { id name } } } } }"}'
```

### Deploy lokálního kódu
```bash
cd /projekt
"C:/Users/tommy/railway.exe" up \
  --project PROJECT_ID \
  --environment ENV_ID \
  --service SERVICE_ID \
  --detach
```

### Propojení projektu (pro příkazy bez --project)
```bash
"C:/Users/tommy/railway.exe" link \
  --project PROJECT_ID \
  --environment ENV_ID \
  --service SERVICE_ID
```

## 4. Env proměnné přes GraphQL API

Railway CLI `variables set` nefunguje dobře bez linku. Používej přímo API:

```bash
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { variableUpsert(input: {projectId: \"P\", environmentId: \"E\", serviceId: \"S\", name: \"KEY\", value: \"VALUE\"}) }"}'
```

Pro Railway reference (např. DATABASE_URL → Postgres service):
```
value: "${{Postgres.DATABASE_URL}}"
```
Pozor: v bash shell expansion — předej přes Python script, ne přes bash heredoc.

## 5. Logy a monitoring

```bash
# Po railway link:
cd /projekt && "C:/Users/tommy/railway.exe" logs

# Nebo přes GraphQL API
```

## 6. Workflow při chybě buildu

1. Zkontroluj logy: `railway logs` (po link)
2. Časté problémy:
   - `requirements.txt` obsahuje balíčky jen pro lokální použití (ib_insync, eventkit) → vytvoř `requirements-web.txt` + `nixpacks.toml` nebo `Dockerfile`
   - Railway ignoruje `nixpacks.toml` pokud používá "railpack" → použij `Dockerfile` pro přesnou kontrolu
3. Oprav, commit, `railway up --detach`

## 7. Veřejná URL

```bash
"C:/Users/tommy/railway.exe" domain
```

## Časté chyby

| Chyba | Příčina | Fix |
|-------|---------|-----|
| `Unauthorized. Please login` | Config v AppData místo ~/.railway | Zapiš config do `~/.railway/config.json` |
| `RAILWAY_TOKEN not working` | Env var nefunguje na Windows bash | Zapiš přímo do config souboru |
| `eventkit>=1.0.4 not found` | ib_insync závisí na neexistující verzi | Vytvoř `requirements-web.txt` bez ib_insync + `Dockerfile` |
| `nixpacks.toml ignorován` | Railway používá interní "railpack" | Použij `Dockerfile` místo nixpacks.toml |
| `FileNotFoundError` | Složka neexistuje | `os.makedirs("logs", exist_ok=True)` |
| `ModuleNotFoundError` | Chybí v requirements | Přidej modul, redeploy |

## IDs pro spread-monitor

Viz `docs/project_notes/key_facts.md`.
