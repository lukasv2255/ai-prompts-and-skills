# Rezervační systém — varianta pro TanStack Start (React + TS)

Alternativa k FastAPI variantě v [SKILL.md](./SKILL.md). Tato verze cílí na projekty postavené na **TanStack Start** (např. Lovable šablona `@lovable.dev/vite-tanstack-config`) — Vite + React 19 + file-based routing + `createServerFn` pro server-side endpoints.

> Funkční vzor je nasazen v projektu `web-redesign-chalupacerna/redesign-whiz/` — single-tenant (jedna chalupa, jedna jednotka). Tento dokument je extrakt zkušeností z toho nasazení.

## Co se liší proti FastAPI variantě
- Backend nejsou Flask/FastAPI endpointy, ale **server functions** přes `createServerFn` (TanStack Start RPC) — volají se z klienta jako běžná async funkce, server-only kód je tree-shaken z bundle.
- SQLite přes **`better-sqlite3`** (synchronní, v Node procesu), ne přes Python `sqlite3`.
- Kalendář přes **`react-day-picker`** (mode="range") namísto Flatpickr. `react-day-picker` je pravděpodobně už v deps (Lovable šablony ho zahrnují) — pokud není, doinstaluj `react-day-picker` + `date-fns`.
- HTML → **JSX/TSX** komponenta jako TanStack route v `src/routes/rezervace.tsx`.
- Žádný HTML šablonový engine — vše React (queries přes `@tanstack/react-query`).

## Předpoklady
- TanStack Start projekt (`vite dev` funguje, `src/routes/` existuje, `routeTree.gen.ts` se generuje)
- Node 20+
- Pokud projekt cílí **Cloudflare Workers** runtime, nelze použít `better-sqlite3` (nativní binárka, Node-only). Pak buď přepni Nitro preset na `node-server`, nebo použij D1/Turso/Neon. Vzor níže předpokládá Node runtime.

## Krok 1 — Závislosti
```bash
npm install better-sqlite3
npm install -D @types/better-sqlite3
# pokud nejsou v deps:
npm install react-day-picker date-fns
```

## Krok 2 — DB modul (`src/lib/reservations-db.ts`)
```ts
import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";

const DB_PATH = resolve(process.cwd(), "data", "reservations.db");

let db: Database.Database | undefined;

export function getDb(): Database.Database {
  if (db) return db;
  mkdirSync(dirname(DB_PATH), { recursive: true });
  db = new Database(DB_PATH);
  db.pragma("journal_mode = WAL");
  db.exec(`
    CREATE TABLE IF NOT EXISTS rezervace (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL,
      jmeno TEXT NOT NULL,
      email TEXT NOT NULL,
      telefon TEXT,
      pokoj TEXT NOT NULL,
      datum_od TEXT NOT NULL,
      datum_do TEXT NOT NULL,
      stav TEXT NOT NULL DEFAULT 'cekajici',
      created_at TEXT NOT NULL
    )
  `);
  return db;
}

export type Rezervace = {
  id: number;
  jmeno: string;
  email: string;
  telefon: string | null;
  pokoj: string;
  datum_od: string;
  datum_do: string;
  stav: "cekajici" | "potvrzeno" | "zruseno";
  created_at: string;
};
```
- Lazy singleton pattern (kontext server functions neumí inicializovat DB při importu modulu — `process.cwd()` je dostupné až za runtime).
- `data/reservations.db` přidej do `.gitignore`.
- **Cesta na produkci:** pokud nasazuješ na Railway s perzistentním Volume, přesměruj `DB_PATH` přes env: `process.env.DB_PATH ?? resolve(process.cwd(), "data", "reservations.db")` a v Railway nastav `DB_PATH=/data/reservations.db`.

## Krok 3 — Server functions (`src/lib/reservations.ts`)
```ts
import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { getDb, type Rezervace } from "./reservations-db";

const SLUG = "chalupa-cerna"; // UPRAV

const RezervaceInputSchema = z.object({
  jmeno: z.string(),
  email: z.string(),
  telefon: z.string().optional().default(""),
  pokoj: z.string(),
  datum_od: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  datum_do: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  token: z.string().optional().default(""),
});

export const listRezervace = createServerFn({ method: "GET" }).handler(
  async (): Promise<Rezervace[]> => {
    const db = getDb();
    return db
      .prepare(
        `SELECT id, jmeno, email, telefon, pokoj, datum_od, datum_do, stav, created_at
         FROM rezervace WHERE slug = ? ORDER BY datum_od ASC`,
      )
      .all(SLUG) as Rezervace[];
  },
);

export const createRezervace = createServerFn({ method: "POST" })
  .inputValidator((input: unknown) => RezervaceInputSchema.parse(input))
  .handler(async ({ data }) => {
    const ownerToken = process.env.OWNER_TOKEN ?? "";
    const jeMajitel = !!data.token && data.token === ownerToken;
    const stavNovy = "potvrzeno"; // instant-book
    const jmeno = data.jmeno || (jeMajitel ? "Blokace" : "");

    if (data.datum_od >= data.datum_do) {
      throw new Error("Datum odjezdu musí být po datu příjezdu.");
    }

    const db = getDb();
    if (!jeMajitel) {
      const konflikt = db
        .prepare(
          `SELECT id FROM rezervace
           WHERE slug = ? AND (pokoj = ? OR pokoj = '*') AND stav = 'potvrzeno'
             AND datum_od < ? AND datum_do > ?`,
        )
        .get(SLUG, data.pokoj, data.datum_do, data.datum_od);
      if (konflikt) throw new Error("Termín je již obsazen pro tento pokoj.");
    }

    db.prepare(
      `INSERT INTO rezervace (slug, jmeno, email, telefon, pokoj, datum_od, datum_do, stav, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    ).run(
      SLUG, jmeno, data.email, data.telefon ?? "", data.pokoj,
      data.datum_od, data.datum_do, stavNovy, new Date().toISOString(),
    );
    return { ok: true as const };
  });

const IdInput = z.object({ id: z.number().int().positive() });

export const potvrditRezervaci = createServerFn({ method: "POST" })
  .inputValidator((input: unknown) => IdInput.parse(input))
  .handler(async ({ data }) => {
    const db = getDb();
    const row = db
      .prepare(`SELECT pokoj, datum_od, datum_do FROM rezervace WHERE id = ? AND slug = ?`)
      .get(data.id, SLUG) as { pokoj: string; datum_od: string; datum_do: string } | undefined;
    if (!row) throw new Error("Rezervace nenalezena.");
    const konflikt = db
      .prepare(
        `SELECT id FROM rezervace
         WHERE slug = ? AND pokoj = ? AND stav = 'potvrzeno' AND id != ?
           AND datum_od < ? AND datum_do > ?`,
      )
      .get(SLUG, row.pokoj, data.id, row.datum_do, row.datum_od);
    if (konflikt) throw new Error("Termín koliduje s jinou potvrzenou rezervací.");
    db.prepare(`UPDATE rezervace SET stav = 'potvrzeno' WHERE id = ? AND slug = ?`).run(data.id, SLUG);
    return { ok: true as const };
  });

export const zrusitRezervaci = createServerFn({ method: "POST" })
  .inputValidator((input: unknown) => IdInput.parse(input))
  .handler(async ({ data }) => {
    const db = getDb();
    db.prepare(`UPDATE rezervace SET stav = 'zruseno' WHERE id = ? AND slug = ?`).run(data.id, SLUG);
    return { ok: true as const };
  });
```

**Pasti při psaní server functions:**
- API je `.inputValidator(fn)` + `.handler(({ data }) => ...)`, **ne** `.validator()` (starší TanStack docs). V handleru data jsou pod `data`, ne přímo v argumentu.
- Z klienta se volají jako `createRezervace({ data: { ... } })`, **ne** `createRezervace({ ... })` — payload vždy v obálce `{ data }`.
- Throwing `Error` v handleru se serializuje do klienta — `e.message` v klientu funguje. Pro 4xx vs 5xx rozlišení použij `redirect()`/`notFound()` z `@tanstack/react-router`, nebo vlastní error class.
- `process.env.X` na serveru čte runtime env, **NE** Vite `import.meta.env` (to je pro klient + jen `VITE_*` prefixed).

## Krok 4 — Frontend route (`src/routes/rezervace.tsx`)

Klíčové části (zkrácené, full vzor viz `redesign-whiz/src/routes/rezervace.tsx`):

```tsx
import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { DayPicker, type DateRange } from "react-day-picker";
import "react-day-picker/style.css";
import { cs } from "date-fns/locale";

import {
  createRezervace, listRezervace, potvrditRezervaci, zrusitRezervaci,
} from "@/lib/reservations";

export const Route = createFileRoute("/rezervace")({
  component: RezervacePage,
});

// Lokální YYYY-MM-DD (vyhnout se UTC shiftu z toISOString())
function toIsoDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}
function parseIsoDate(s: string): Date {
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
}
function eachDate(fromInclusive: Date, toExclusive: Date): Date[] {
  const out: Date[] = []; const d = new Date(fromInclusive);
  while (d < toExclusive) { out.push(new Date(d)); d.setDate(d.getDate() + 1); }
  return out;
}

function RezervacePage() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["rezervace"], queryFn: () => listRezervace() });
  const reservations = q.data ?? [];

  // Hotelová konvence: den X je disabled iff je morning-claimed AND evening-claimed
  //   arrival (od)       = evening claim
  //   departure (do)     = morning claim
  //   středové noci      = morning + evening
  const blockedDateSet = useMemo(() => {
    const morning = new Set<string>();
    const evening = new Set<string>();
    for (const r of reservations) {
      if (r.stav !== "potvrzeno") continue;
      const od = parseIsoDate(r.datum_od);
      const doD = parseIsoDate(r.datum_do);
      for (const d of eachDate(od, doD)) evening.add(toIsoDate(d));
      for (const d of eachDate(
        new Date(od.getFullYear(), od.getMonth(), od.getDate() + 1),
        new Date(doD.getFullYear(), doD.getMonth(), doD.getDate() + 1),
      )) morning.add(toIsoDate(d));
    }
    const blocked = new Set<string>();
    for (const d of morning) if (evening.has(d)) blocked.add(d);
    return blocked;
  }, [reservations]);

  const isDateBlocked = (d: Date) => blockedDateSet.has(toIsoDate(d));

  const [range, setRange] = useState<DateRange | undefined>();
  const createMut = useMutation({
    mutationFn: (data: /* ...payload... */ any) => createRezervace({ data }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rezervace"] }),
  });

  return (
    <DayPicker
      mode="range" selected={range} onSelect={setRange}
      locale={cs} weekStartsOn={1}
      disabled={[{ before: new Date() }, isDateBlocked]}
    />
    /* ... formulářové inputy, tabulka rezervací, owner panel ... */
  );
}
```

**Klíčové detaily:**
- `disabled` v `DayPicker` přijímá pole matcherů — kombinuj `{ before: today }` s vlastním predikátem `isDateBlocked`.
- `weekStartsOn={1}` = pondělí (CZ konvence).
- `locale={cs}` z `date-fns/locale` — `react-day-picker` interně formátuje měsíce/dny touto locale.
- **NIKDY** nepoužij `d.toISOString().slice(0,10)` — způsobí shift přes timezone (host v UTC+2 vybere 16., dostane 15.). Lokální `getFullYear/getMonth/getDate` jediné správné řešení.
- `@/lib/reservations` — `@` alias je nastaven v Vite konfigu Lovable šablon automaticky.

## Krok 5 — Owner panel (blokace majitelem)
```tsx
const ownerToken =
  typeof window !== "undefined"
    ? new URLSearchParams(window.location.search).get("token") ?? ""
    : "";
const isOwner = !!ownerToken;

// V handleru submitOwner pošli pokoj: "*" pro "Všechny pokoje" + token: ownerToken
// Server function pak vyhodnotí jeMajitel a uloží jako 'potvrzeno' s jmeno='Blokace'.
```
- `typeof window !== "undefined"` chrání SSR (route je `createFileRoute`, runs server-side při prvním requestu).
- Admin tabulka zobrazí sloupec "Akce" (Potvrdit/Zrušit) jen pokud `isOwner`.

## Volba modelu — instant-book vs poptávkový
Stejné jako u FastAPI varianty. Default = instant-book (`stavNovy = "potvrzeno"`). Pro poptávkový změň na `const stavNovy = jeMajitel ? "potvrzeno" : "cekajici"` a odeber konflikt-check pro hosty (jinak druhá poptávka na stejný termín spadne na 409 i když by se mohla čekat ve frontě).

## Hotelová konvence — vysvětlení logiky
Naivní přístup ("zablokuj všechny dny od `datum_od` do `datum_do`") rozbije navazující rezervace: host A odjíždí 18. ráno, host B přijíždí 18. večer — oba mají právo na den 18.

Správné řešení modeluje **dvě části dne**:
- **morning claim** = `datum_od + 1 ... datum_do` (každá rezervace si nárokuje "ráno" každého dne po příjezdu až do dne odjezdu včetně)
- **evening claim** = `datum_od ... datum_do - 1` (každá rezervace si nárokuje "večer" od dne příjezdu až do dne před odjezdem)
- **disabled** = den má morning **i** evening claim (od jakékoli rezervace)

Důsledek:
- 1 rezervace 16.–18.: morning={17,18}, evening={16,17} → blocked={17}
- Po přidání 18.–20.: morning={17,18,19,20}, evening={16,17,18,19} → blocked={17,18,19} ✓

Ten samý vzorec funguje s `pokoj` granularitou — drž `morning`/`evening` mapy per-pokoj a vyhodnocuj kalendář vždy pro aktuálně zvolený pokoj.

## Wire-up do existujícího webu
1. Tlačítko/odkaz "Rezervovat" z hero/CTA: `<Link to="/rezervace">Rezervovat termín</Link>` (TanStack `Link`, ne `<a>`).
2. Pokud má homepage placeholder kalendář s hardcoded daty (typické u Lovable šablon), vyhoď ho — nový `/rezervace` view ho nahrazuje.

## Checklist pro nový projekt
1. `npm install better-sqlite3 @types/better-sqlite3` (případně `react-day-picker date-fns`)
2. `src/lib/reservations-db.ts` — zkopíruj výše, případně přepiš `DB_PATH` přes env
3. `src/lib/reservations.ts` — zkopíruj, **uprav `SLUG`** na slug projektu
4. `src/routes/rezervace.tsx` — zkopíruj z `redesign-whiz/`, **uprav `POKOJE`** seznam
5. Propoj odkazy z existujících routes (CTA, hero, footer)
6. Nastav `OWNER_TOKEN` env proměnnou (`.env` lokálně, Railway/Vercel dashboard pro produkci)
7. Otevři `http://localhost:5174/rezervace?token=OWNER_TOKEN` → owner panel se objeví
8. Přidej `data/` do `.gitignore`

## Pasti specifické pro TanStack Start
- **`routeTree.gen.ts` se regeneruje** — needitovat ručně. Po přidání `src/routes/rezervace.tsx` HMR sám aktualizuje route tree.
- **`createServerFn` musí být importovaná, ne re-deklarovaná** — častý omyl: zkopírovat skeleton z dokumentace, zapomenout import → tichá chyba "createServerFn is not a function".
- **`better-sqlite3` v dev modu** — Vite ho nesmí pre-bundle. Pokud dostaneš `Error: Module did not self-register`, přidej do `vite.config.ts`: `optimizeDeps: { exclude: ["better-sqlite3"] }`. V Lovable šabloně to obvykle není potřeba (Vite ho rozpozná jako Node-only přes `external`).
- **SSR + `window`** — owner token čte `window.location.search`. Bez `typeof window !== "undefined"` checku spadne hydratace.
- **Tailwind v4** (Lovable šablona) — používá `@theme inline` s CSS proměnnými, ne `tailwind.config.js`. Vlastní barvy (`bg-success`, `bg-busy`) musí být registrované přes `--color-success` v `styles.css`.

## Tracking maily (Resend)
Stejný princip jako u FastAPI varianty — viz [SKILL.md § Krok 3](./SKILL.md). V TS je rozhraní:
```ts
// src/lib/mail.ts
export async function sendEmail(opts: { to: string; subject: string; html: string; replyTo?: string }) {
  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.MAIL_FROM;
  if (!apiKey || !from) {
    console.log(`MAIL log-only → komu=${opts.to} předmět=${opts.subject}`);
    return false;
  }
  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Authorization": `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from, to: [opts.to], subject: opts.subject, html: opts.html, reply_to: opts.replyTo }),
  });
  return resp.ok;
}
```
A volej z `createRezervace` handleru **po** `INSERT` (mailové selhání nesmí shodit uloženou rezervaci — wrap v try/catch).

## Reference implementace
`/Users/lukas/Můj disk/web-redesign/web-redesign-chalupacerna/redesign-whiz/`:
- `src/lib/reservations-db.ts`
- `src/lib/reservations.ts`
- `src/routes/rezervace.tsx`
- `src/routes/index.tsx` (wire-up CTA)
