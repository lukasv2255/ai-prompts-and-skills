---
name: lovable-railway-deploy
description: Nasaď Lovable TanStack template (`@lovable.dev/vite-tanstack-config`) na Railway. Použij když uživatel chce deploynout projekt naklonovaný z Lovable (typicky se sděleními "deploy na railway", "nasaď ten template", "lovable na railway") a v `vite.config.ts` se importuje `@lovable.dev/vite-tanstack-config`.
allowed-tools: Bash, Read, Edit, Write, Glob
---

# Lovable TanStack template → Railway deploy

## Kdy spustit

Spusť pokud projekt obsahuje:
- `vite.config.ts` s `from "@lovable.dev/vite-tanstack-config"`
- `package.json` s `@tanstack/react-start` v deps
- typicky chybí `start` script

## Klíčové gotchas (proč to bez zásahu spadne)

1. **Lovable config defaultně buildí pro Cloudflare Workers**, ne Node. Build output `dist/server/server.js` je `export default { fetch }` handler — žádný Node HTTP listener. Když to spustíš `node dist/server/server.js`, modul se načte a proces skončí. Railway healthcheck → 502.
2. **Chybí start script.** Railpack auto-detektuje Node a po buildu hledá `npm start`. Bez něj kontejner nic nespustí.
3. **Pozor na cached Railway service.** Pokud projekt re-linkneš na starou službu která byla původně Python/FastAPI, Railpack vytáhne cached pip/requirements a build je matoucí (instaluje openai, fastapi). Vždy `railway init` nový projekt nebo zkontroluj logs.
4. **`bun.lock` musí být v sync s `package.json`.** Lovable templates obsahují `bun.lock` — Railpack ho detekuje a build běží přes `bun install --frozen-lockfile`. Pokud kdokoli přidá dep do `package.json` (např. `flatpickr`) jen přes `npm install`, `bun.lock` se neaktualizuje a build padne na:
   ```
   error: lockfile had changes, but lockfile is frozen
   process "bun install --frozen-lockfile" did not complete successfully
   ```
   Aktivní zůstane poslední úspěšný deploy → `railway up` "vypadá že prošel", ale produkce stále servíruje starý kód. Vždy regeneruj `bun.lock` přes `bun install` po každé změně `package.json`, jinak deploy tiše selže a CDN servíruje stale build.
5. **npm varianta: `package-lock.json` out of sync s Nitro runtime deps.** Když projekt jede na npm (`package-lock.json`, žádný `bun.lock`), railpack použije Nitro provider: po `npm run build` vygeneruje `.output/server/package.json` s **přesně pinnutými** runtime verzemi (např. `lru-cache@11.5.1`) a v runtime stage proti němu pustí `npm ci`. Pokud root `package-lock.json` tu přesnou tranzitivní verzi nemá (lock nebyl regenerován po bumpu deps), build padne na:
   ```
   npm error `npm ci` can only install packages when your package.json and
   package-lock.json ... are in sync.
   npm error Missing: lru-cache@11.5.1 from lock file
   ```
   **Pozor:** lokálně `npm ci --dry-run` může projít a `npm install` napíše "up to date" — protože lokální tree je vyřešený jinak. To NEopraví pin. Spolehlivý fix je regenerace lockfile načisto:
   ```bash
   rm -f package-lock.json && rm -rf node_modules && npm install
   grep -c "lru-cache-11.5" package-lock.json   # ověř že přesná verze je v locku
   ```
   Tím se tranzitivní deps vyřeší na nejnovější matching verze, které sednou s tím co Nitro pinuje. Pak teprve `railway up --ci`.
6. **Vite dev `server.proxy` je DEV-ONLY — v produkci `/api` spadne na 404.** Lovable frontendy často volají backend relativně (`fetch("/api/rezervace/{slug}")`) a v `vite.config.ts` mají `vite: { server: { proxy: { "/api": ... } } }`. Tahle proxy běží **jen v `vite dev`**. Produkční Nitro node-server o `/api` neví → vrací **404**, tabulky zůstanou prázdné a formuláře nejdou odeslat. Build i healthcheck přitom projdou, takže to vypadá jako úspěšný deploy. Fix = **Nitro `routeRules` proxy** (viz krok 8) — drží relativní `/api`, žádné CORS, žádný zásah do frontend kódu (který typicky vlastní Lovable a přepisuje ho).
7. **Lovable přepisuje `package-lock.json` / `vite.config.ts` na pozadí (Google Drive sync).** Projekty naklonované z Lovable bývají ve složce synced přes Google Drive (`~/.../Můj disk/...`). Lovable sync **kdykoli během práce** přegeneruje `package-lock.json` (zahodí lru-cache pin z gotcha #5) a může přepsat i `vite.config.ts` (zahodí `nitro` blok a `routeRules`). Důsledek: regeneruješ lock, ověříš, ale než stihneš `railway up`, Lovable ho přepíše zpět → deploy zase padne na `npm ci`. **Proto regeneraci locku a `railway up` pouštěj back-to-back v jednom kroku** (viz krok 5) a po deployi ověř, že `nitro`/`routeRules` ve `vite.config.ts` pořád jsou.

## Postup (deterministicky)

### 1. Přepni Nitro preset na node-server

V `vite.config.ts` přidej `nitro: { preset: "node-server" }`:

```ts
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    server: { entry: "server" },
  },
  nitro: {
    preset: "node-server",
  },
});
```

Po této změně build vyrobí standardní Nitro Node output: `.output/server/index.mjs` — respektuje `PORT` env, listenuje na `0.0.0.0`, gracefull shutdown.

### 2. Přidej start script do package.json

```json
{
  "scripts": {
    "build": "vite build",
    "start": "node .output/server/index.mjs"
  }
}
```

### 3. Lokální smoke test (povinný před `railway up`)

```bash
rm -rf dist .output
npm run build
PORT=8090 node .output/server/index.mjs &
sleep 4
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8090/
pkill -f ".output/server/index.mjs"
```

Očekávej `HTTP 200`. Pokud něco jiného, build je špatně — nepouštěj na Railway.

### 3b. Sync bun.lock (pokud byly změny v package.json)

Jakmile přidáš/odebereš dep v `package.json`, regeneruj `bun.lock` před deployem:

```bash
# pokud nemáš bun:
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.bun/bin:$PATH"

bun install   # aktualizuje bun.lock podle package.json
grep -c <nazev_balicku> bun.lock   # ověř že balíček je v lockfile
```

Bez tohoto kroku `railway up --ci` projde upload fází, ale build na Railway selže s `lockfile had changes, but lockfile is frozen` — a produkce zůstane na starém deployi.

### 3c. Sync package-lock.json (npm projekty bez bun.lock)

Pokud projekt nemá `bun.lock` (jede na npm), regeneruj lockfile načisto před deployem — jinak `npm ci` na Railway padne na nesouladu s Nitro runtime piny (viz gotcha #5):

```bash
rm -f package-lock.json && rm -rf node_modules && npm install
npm ci --dry-run   # musí projít bez EUSAGE
```

### 4. Vytvoř nový Railway projekt (nemíchat s existujícími službami)

Pokud projekt už není linknutý na Railway:

```bash
railway init --name <project-slug>
```

Pokud je linknutý na starou službu:

```bash
railway unlink --yes
railway init --name <project-slug>
```

### 5. Deploy

U npm projektů z Lovable spusť regeneraci locku a deploy **v jednom řetězci**, aby Lovable sync (gotcha #7) nestihl lock mezitím přepsat:

```bash
# regeneruj lock JEN když chybí pin, a hned deployuj:
if [ "$(grep -c 'lru-cache-11.5' package-lock.json)" -eq 0 ]; then
  rm -f package-lock.json && rm -rf node_modules && npm install
fi
railway up --ci
```

Railpack detekuje Node 22, spustí `npm install` + `npm run build` a poté `npm start`. Build trvá 2-3 min.

### 6. Veřejná doména

`railway init` službu nevyrobí automaticky — `railway up` ji vytvoří a pojmenuje podle projektu. Po `railway up` přilinkuj službu:

```bash
railway service <service-name>   # typicky stejné jako project name
railway domain                   # vyrobí *.up.railway.app
```

### 7. Verifikace

```bash
sleep 12   # cold start
curl -s -L -o /dev/null -w "HTTP %{http_code}\n" https://<service>-production.up.railway.app/
```

Při 502 stáhni runtime logy: `railway logs --deployment`. Bývá to:
- chybí PORT binding (špatný preset)
- crash při SSR (mrkni do `src/server.ts` error wrapperu)

### 8. Produkční proxy `/api` na backend (když frontend volá relativní API)

Pokud frontend fetchuje `/api/...` a v dev to řeší `vite.server.proxy` (gotcha #6), přidej do `nitro` v `vite.config.ts` `routeRules` proxy na **nasazený** backend. Tím produkční Nitro server forwarduje `/api/**` (vč. POST/PATCH) na backend — relativní fetch funguje, bez CORS:

```ts
nitro: {
  preset: "node-server",
  routeRules: {
    "/api/**": {
      proxy: "https://<backend>-production.up.railway.app/api/**",
    },
  },
},
```

Backend bývá samostatný projekt (např. FastAPI), často **už nasazený** na Railway — najdi ho:
```bash
# který proces drží dev backend a kde má zdroják:
lsof -i:8000 -sTCP:LISTEN; ps -o command= -p <PID>
# v té složce zjisti nasazenou doménu:
cd <backend-dir> && railway domain
```
Smoke test (lokální prod build proxuje na ŽIVÝ backend — vrátí reálná data):
```bash
npm run build && PORT=8092 node .output/server/index.mjs &
curl -s http://localhost:8092/api/rezervace/<slug> | head -c 200
```
Po deployi ověř na produkci: `curl https://<frontend>.up.railway.app/api/rezervace/<slug>` musí vrátit JSON, ne 404.

> **Pozor (gotcha #7):** `routeRules` je ve `vite.config.ts`, který Lovable přepisuje. Po každém Lovable syncu zkontroluj, že blok pořád existuje, jinak `/api` na produkci zase spadne na 404.

### Diagnostika FAILED deploye (proč `railway logs` klame)

`railway logs --deployment` ukazuje logy **AKTIVNÍHO** (posledního úspěšného) deploye — NE toho, co právě selhal. Failed deploy tak vypadá, že "běží a listenuje", ačkoli ve skutečnosti spadl při buildu. Skutečnou příčinu vytáhni přes GraphQL podle deployment ID (z `Build Logs:` URL v outputu `railway up`):

```bash
TOKEN=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.railway/config.json')))['user']['token'])")
DID=<deployment-id>
# status:
curl -s -X POST https://backboard.railway.app/graphql/v2 -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"query { deployment(id: \\\"$DID\\\") { status } }\"}"
# build logy (tady je skutečná chyba, typicky npm ci / lru-cache):
curl -s -X POST https://backboard.railway.app/graphql/v2 -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"query { buildLogs(deploymentId: \\\"$DID\\\", limit: 40) { message } }\"}" \
  | python3 -c "import sys,json;[print(l['message']) for l in json.load(sys.stdin)['data']['buildLogs']]"
```

Když je `status: FAILED` a `deploymentLogs` jsou prázdné → spadl v build/install fázi (ne runtime). Skoro vždy je to gotcha #4/#5 (out-of-sync lockfile).

### Když produkce servíruje starý kód po `railway up`

Symptom: deploy "projde" (CLI vypíše Build Logs URL, exit 0), ale produkční HTML/bundle hash se nemění. Diagnostika:

```bash
# Stáhni HTML a porovnej bundle hash s lokálním buildem
curl -s --compressed https://<service>.up.railway.app/ -o /tmp/prod.html
grep -aoE 'index-[A-Za-z0-9_]+\.js' /tmp/prod.html | sort -u
ls .output/public/assets/ | grep "index-" | sort -u
```

Pokud hashes nesedí, deploy selhal. Kontrola na dashboard URL → většinou `bun install --frozen-lockfile` exit code. **Trvalý fix**: regeneruj `bun.lock` (viz krok 3b). `railway redeploy` ani opakované `railway up` to nevyřeší — protože re-deployují stejný broken commit nebo stejně out-of-sync source.

## Reference

- Lovable config types: `node_modules/@lovable.dev/vite-tanstack-config/dist/index.d.ts` — `nitro` option
- Nitro presety: `node-server`, `node-cluster`, `vercel`, `netlify`, `cloudflare-module` (default Lovable)
- Při Cloudflare deployi (pokud bys nechtěl Railway): standardní `wrangler deploy` na `dist/server/server.js`
