---
name: rezervacni-system-ubytovani
description: Přidá rezervační systém pro ubytování (chalupa, apartmán, penzion) — FastAPI + SQLite + HTML UI s Flatpickr kalendářem, blokováním obsazených termínů a admin akcemi Potvrdit/Zrušit. Pro React/TanStack Start projekty viz TANSTACK_START.md.
---

# Rezervační systém — ubytování (FastAPI + SQLite)

Přidá funkční rezervační systém do projektu s FastAPI backendem a HTML stránkou (formulář + jednoduchý admin přehled). Určeno pro chalupy, apartmány, penziony — rezervace po nocích s výběrem pokoje.

> **Než začneš — zkontroluj stack hostujícího projektu:**
> - **Python FastAPI + HTML šablona / Jinja preview** → pokračuj tímto SKILL.md (default).
> - **React / TanStack Start / Vite (např. Lovable šablona `@lovable.dev/vite-tanstack-config`)** → přepni na [TANSTACK_START.md](./TANSTACK_START.md). Ten popisuje variantu se `createServerFn`, `better-sqlite3` a `react-day-picker` namísto FastAPI + Flatpickr. Logika (instant-book, hotelová konvence, owner token) je stejná, implementace jiná.
> - **Pro produkční nasazení s plnohodnotným admin loginem** (více účtů, per-tenant ACL přes slug, bcrypt hesla, signed session cookie, CSRF, rate limit, reset přes email) → viz [ADMIN_AUTH.md](./ADMIN_AUTH.md). Tento SKILL.md popisuje základní variantu s `OWNER_TOKEN` v URL (vhodné pro rychlé demo / preview).

## Co systém umí
- Formulář s výběrem pokoje, termínu (Flatpickr), jména, emailu, telefonu
- **Instant-book (default):** host odešle formulář → termín je okamžitě `potvrzeno` v DB a zablokovaný pro ostatní hosty. Žádná manuální správa majitelem; viz „Volba modelu" níže pokud potřebuješ jinou variantu.
- Potvrzené termíny jsou vizuálně blokované v kalendáři pro hosty (nelze vybrat)
- **Hotelová konvence dnů** — den příjezdu i den odjezdu zůstávají klikatelné (host přijíždí večer, předchozí host odjel ráno). Zašedne jen středová „noc". Rezervace 16.–18. blokuje pouze 17.; po přidání 18.–20. zašedne i 18.
- Různé pokoje lze rezervovat na stejný termín nezávisle
- Admin tabulka s tlačítky `Potvrdit` / `Zrušit` (pro ruční korekce — no-show, refundace)
- **Blokace majitelem:** vlastní formulář v admin sekci — majitel vybere datum od/do, pokoj (nebo "Všechny pokoje"), klikne Zablokovat → termín se okamžitě zablokuje v kalendáři hostů bez čekání na potvrzení
- **Tracking notifikace mailem (volitelné, Krok 3):** po odeslání poptávky systém pošle 2 maily přes Resend — (a) "engagement signal" interní notifikaci, (b) potvrzení hostovi z ověřené domény. V preview/demo režimu hardcoded adresy → měříš kolik leadů reálně vyplnilo formulář.
- SQLite databáze, WAL mode

## Volba modelu — instant-book vs poptávkový

Před nasazením promysli s majitelem, jaký model chce. Default skillu = **B (instant-book)**, protože nevyžaduje žádnou manuální správu a host má hned jistotu. Změna na A je triviální (jeden řetězec v `INSERT`).

### A) Soft-hold (poptávkový)
- POST ukládá `stav='cekajici'`, termín se NEblokuje
- Více hostů může poptat stejné dny, majitel si vybere a jednu potvrdí
- Hodí se když: majitel chce preferovat delší pobyty / lepší hosty / mít finální slovo
- Implementace: změň `stav_novy = "potvrzeno" if je_majitel else "potvrzeno"` zpět na `… else "cekajici"` a uprav success hlášku ve frontendu na *„Poptávka odeslána, termín bude potvrzen do 24h."*

### B) Instant-book (default)
- POST ukládá rovnou `stav='potvrzeno'`, termín se zablokuje okamžitě
- Kdo dřív POSTne, ten dostane termín (souběh řeší SQL kontrola kolize → druhý host dostane 409)
- Hodí se když: majitel chce minimum práce, OK když vyhraje rychlejší host
- Admin tlačítka `Potvrdit`/`Zrušit` zůstávají pro ruční korekce (no-show, refundace).

## Předpoklady (navíc)
- `OWNER_TOKEN` env proměnná — libovolný tajný řetězec, majitel ho zadá do URL admin sekce

## Předpoklady
- Běží FastAPI aplikace (např. `server.py` / `main.py`) a už máš nastavené základní routování
- Máš `sqlite3` + `datetime` + `timezone` importy (doplníš podle potřeby)
- Máš v projektu nějaký HTML soubor/sekci, kam vložíš UI blok (nebo templating)

## Krok 1 — Backend (FastAPI)

### Závislosti (přidat k importům pokud chybí)
```python
from pydantic import BaseModel
```

### Cesta k DB
Přidej k ostatním DB cestám.

Poznámka: `BASE_DIR` si ponech podle struktury projektu (typicky kořen repa).
```python
RESERVATIONS_DB = BASE_DIR / "data" / "reservations.db"
```

### Endpointy (přidat na konec souboru)
```python
# ─── REZERVAČNÍ SYSTÉM ───────────────────────────────────────────────────────

class RezervaciData(BaseModel):
    jmeno: str
    email: str
    telefon: str
    pokoj: str      # konkrétní pokoj nebo "*" = všechny pokoje (jen pro blokaci majitelem)
    datum_od: str   # formát YYYY-MM-DD
    datum_do: str   # formát YYYY-MM-DD
    token: str = "" # owner token — pokud shodný s OWNER_TOKEN env, vytvoří blokaci rovnou potvrzenou


def _ensure_rezervace_schema(conn: sqlite3.Connection):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
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
    """)
    try:
        conn.execute("ALTER TABLE rezervace ADD COLUMN stav TEXT NOT NULL DEFAULT 'cekajici'")
    except Exception:
        pass


@app.post("/api/rezervace/{slug}")
def create_rezervace(slug: str, data: RezervaciData):
    import os
    je_majitel = bool(data.token and data.token == os.getenv("OWNER_TOKEN", ""))
    stav_novy = "potvrzeno" if je_majitel else "cekajici"
    jmeno = data.jmeno or ("Blokace" if je_majitel else "")

    RESERVATIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        # Hosté nesmí rezervovat termín blokovaný majitelem (pokoj="*" = celý objekt)
        if not je_majitel:
            konflikt = conn.execute("""
                SELECT id FROM rezervace
                WHERE slug = ? AND (pokoj = ? OR pokoj = '*') AND stav = 'potvrzeno'
                  AND datum_od < ? AND datum_do > ?
            """, (slug, data.pokoj, data.datum_do, data.datum_od)).fetchone()
            if konflikt:
                raise HTTPException(status_code=409, detail="Termín je již obsazen pro tento pokoj.")
        conn.execute("""
            INSERT INTO rezervace (slug, jmeno, email, telefon, pokoj, datum_od, datum_do, stav, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            slug, jmeno, data.email, data.telefon,
            data.pokoj, data.datum_od, data.datum_do, stav_novy,
            datetime.now(timezone.utc).isoformat()
        ))
    return {"ok": True}


@app.get("/api/rezervace/{slug}")
def get_rezervace(slug: str):
    RESERVATIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        rows = conn.execute("""
            SELECT id, jmeno, email, telefon, pokoj, datum_od, datum_do, stav, created_at
            FROM rezervace WHERE slug = ?
            ORDER BY datum_od ASC
        """, (slug,)).fetchall()
    return JSONResponse([{
        "id": r[0], "jmeno": r[1], "email": r[2], "telefon": r[3],
        "pokoj": r[4], "datum_od": r[5], "datum_do": r[6],
        "stav": r[7], "created_at": r[8]
    } for r in rows])


@app.patch("/api/rezervace/{slug}/{rezervace_id}/potvrdit")
def potvrdit_rezervaci(slug: str, rezervace_id: int):
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        row = conn.execute(
            "SELECT pokoj, datum_od, datum_do FROM rezervace WHERE id = ? AND slug = ?",
            (rezervace_id, slug)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Rezervace nenalezena.")
        pokoj, datum_od, datum_do = row
        konflikt = conn.execute("""
            SELECT id FROM rezervace
            WHERE slug = ? AND pokoj = ? AND stav = 'potvrzeno' AND id != ?
              AND datum_od < ? AND datum_do > ?
        """, (slug, pokoj, rezervace_id, datum_do, datum_od)).fetchone()
        if konflikt:
            raise HTTPException(status_code=409, detail="Termín koliduje s jinou potvrzenou rezervací.")
        conn.execute(
            "UPDATE rezervace SET stav = 'potvrzeno' WHERE id = ? AND slug = ?",
            (rezervace_id, slug)
        )
    return {"ok": True}


@app.patch("/api/rezervace/{slug}/{rezervace_id}/zrusit")
def zrusit_rezervaci(slug: str, rezervace_id: int):
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        conn.execute(
            "UPDATE rezervace SET stav = 'zruseno' WHERE id = ? AND slug = ?",
            (rezervace_id, slug)
        )
    return {"ok": True}
```

## Krok 2 — UI blok (HTML)

Vlož do HTML (preview stránky / šablony). Nezapomeň upravit:
- `R_SLUG` (slug projektu)
- seznam pokojů v `<select>`
- případně CSS proměnné (`--green`, `--cream`, …) podle design systému projektu

```html
<!-- ─── REZERVAČNÍ SYSTÉM ───────────────────────────────────────────────── -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/cs.js"></script>

<style>
  :root {
    --white:#fff; --cream:#f8fafc; --text:#0f172a; --muted:#475569;
    --border:#e2e8f0; --green:#0f766e; --green-light:#115e59;
    --radius: 20px; --radius-sm: 12px;
  }
  .rezervace-section { max-width: 920px; margin: 0 auto; padding: 40px 18px; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; color: var(--text); }
  .rezervace-section h2 { font-size: 2rem; margin: 0 0 8px; }
  .rezervace-section .subtitle { color: var(--muted); margin: 0 0 26px; }
  .rezervace-form { background: var(--cream); border: 1px solid var(--border); border-radius: var(--radius); padding: 32px; margin-bottom: 48px; }
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .form-grid .full { grid-column: 1 / -1; }
  .fg { display: flex; flex-direction: column; gap: 6px; }
  .fg label { font-size: 0.85rem; font-weight: 600; color: var(--text); }
  .fg input, .fg select { padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 0.95rem; font-family: inherit; background: var(--white); color: var(--text); outline: none; transition: border-color .2s; }
  .fg input:focus, .fg select:focus { border-color: var(--green); }
  .btn-rezervovat { margin-top: 20px; width: 100%; padding: 14px; background: var(--green); color: #fff; border: none; border-radius: var(--radius-sm); font-size: 1rem; font-weight: 600; cursor: pointer; transition: background .2s; }
  .btn-rezervovat:hover { background: var(--green-light); }
  .btn-rezervovat:disabled { background: #9ca3af; cursor: not-allowed; }
  .form-msg { margin-top: 14px; padding: 12px 16px; border-radius: var(--radius-sm); font-size: 0.9rem; display: none; }
  .form-msg.ok  { background: #ecfdf5; color: #065f46; border: 1px solid #6ee7b7; display: block; }
  .form-msg.err { background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; display: block; }
  .rezervace-table-wrap h3 { font-size: 1.2rem; font-weight: 700; margin-bottom: 16px; color: var(--text); }
  .r-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; background: var(--white); border-radius: var(--radius-sm); overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-bottom: 60px; }
  .r-table th { background: var(--green); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
  .r-table td { padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: middle; }
  .r-table tr:last-child td { border-bottom: none; }
  .stav-badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; color: #fff; white-space: nowrap; }
  .stav-cekajici  { background: #f59e0b; }
  .stav-potvrzeno { background: #22c55e; }
  .stav-zruseno   { background: #ef4444; }
  .btn-akce { padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: none; cursor: pointer; margin-right: 4px; transition: opacity .15s; }
  .btn-akce:hover { opacity: 0.8; }
  .btn-potvrdit { background: #22c55e; color: #fff; }
  .btn-zrusit   { background: #ef4444; color: #fff; }
  .btn-akce:disabled { opacity: 0.4; cursor: not-allowed; }
  @media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }
</style>

<section class="rezervace-section" id="rezervace-system">
  <h2>Rezervace termínu</h2>
  <p class="subtitle">Vyplňte poptávku — po potvrzení se termín zablokuje pro ostatní hosty.</p>

  <div class="rezervace-form">
    <div class="form-grid">
      <div class="fg">
        <label>Datum příjezdu</label>
        <input type="text" id="r-od" placeholder="dd.mm.rrrr" readonly required>
      </div>
      <div class="fg">
        <label>Datum odjezdu</label>
        <input type="text" id="r-do" placeholder="dd.mm.rrrr" readonly required>
      </div>
      <div class="fg full">
        <label>Pokoj</label>
        <select id="r-pokoj">
          <!-- UPRAV: seznam pokojů klienta -->
          <option>Pokoj 1</option>
          <option>Pokoj 2</option>
        </select>
      </div>
      <div class="fg">
        <label>Jméno a příjmení</label>
        <input type="text" id="r-jmeno" placeholder="Jan Novák" required>
      </div>
      <div class="fg">
        <label>Telefon</label>
        <input type="tel" id="r-telefon" placeholder="+420 777 000 000">
      </div>
      <div class="fg full">
        <label>E-mail</label>
        <input type="email" id="r-email" placeholder="jan@novak.cz" required>
      </div>
    </div>
    <button class="btn-rezervovat" id="r-btn" onclick="rOdeslat()">Odeslat poptávku</button>
    <div class="form-msg" id="r-msg"></div>
  </div>

  <div class="rezervace-table-wrap">
    <h3>Přehled rezervací</h3>
    <table class="r-table">
      <thead>
        <tr>
          <th>#</th><th>Pokoj</th><th>Příjezd</th><th>Odjezd</th>
          <th>Jméno</th><th>E-mail</th><th>Telefon</th><th>Stav</th><th>Akce</th>
        </tr>
      </thead>
      <tbody id="r-tbody"><tr><td colspan="9" style="color:#9ca3af;padding:14px">Načítám…</td></tr></tbody>
    </table>
  </div>

  <!-- ── BLOKACE MAJITELEM — zobrazí se jen pokud URL obsahuje ?token=... ── -->
  <div class="rezervace-form" id="bl-panel" style="display:none;border-color:#f59e0b">
    <h3 style="margin:0 0 18px;font-size:1.1rem">Zablokovat termín (majitel)</h3>
    <div class="form-grid">
      <div class="fg">
        <label>Od</label>
        <input type="text" id="bl-od" placeholder="dd.mm.rrrr" readonly required>
      </div>
      <div class="fg">
        <label>Do</label>
        <input type="text" id="bl-do" placeholder="dd.mm.rrrr" readonly required>
      </div>
      <div class="fg full" id="bl-pokoj-wrap">
        <label>Pokoj</label>
        <select id="bl-pokoj">
          <!-- UPRAV: stejný seznam pokojů jako výše -->
          <option>Pokoj 1</option>
          <option>Pokoj 2</option>
        </select>
      </div>
      <div class="fg full">
        <label style="flex-direction:row;align-items:center;gap:8px;cursor:pointer">
          <input type="checkbox" id="bl-vse" onchange="blVseChange()"> Všechny pokoje
        </label>
      </div>
    </div>
    <button class="btn-rezervovat" id="bl-btn" onclick="blOdeslat()" style="background:#f59e0b">Zablokovat termín</button>
    <div class="form-msg" id="bl-msg"></div>
  </div>
</section>

<script>
  const R_SLUG = 'NAZEV_SLUG';  // ← UPRAV
  let vsechnyRezervace = [];

  const fpOd = flatpickr('#r-od', {
    locale: 'cs', dateFormat: 'Y-m-d', altInput: true, altFormat: 'd.m.Y',
    minDate: 'today',
    onChange: function(dates) { if (dates[0]) fpDo.set('minDate', dates[0]); }
  });
  const fpDo = flatpickr('#r-do', {
    locale: 'cs', dateFormat: 'Y-m-d', altInput: true, altFormat: 'd.m.Y',
    minDate: 'today'
  });

  function ziskatObsazene(pokoj) {
    // zahrnout i blokace majitelem pro všechny pokoje (pokoj = '*')
    return vsechnyRezervace
      .filter(r => r.stav === 'potvrzeno' && (r.pokoj === pokoj || r.pokoj === '*'))
      .map(r => ({ from: r.datum_od, to: r.datum_do }));
  }

  function aktualizovatKalendar() {
    const pokoj = document.getElementById('r-pokoj').value;
    const obsazene = ziskatObsazene(pokoj);
    fpOd.set('disable', obsazene); fpDo.set('disable', obsazene);
    fpOd.clear(); fpDo.clear();
  }

  document.getElementById('r-pokoj').addEventListener('change', aktualizovatKalendar);

  // XSS prevention — hodnoty z API jdou do innerHTML, MUSÍME escapovat.
  // Bez toho by host s `<script>` ve jméně spustil JS každému návštěvníkovi.
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g,
      c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  async function rNacist() {
    try {
      const res = await fetch(`/api/rezervace/${R_SLUG}`);
      const data = await res.json();
      vsechnyRezervace = data;
      aktualizovatKalendar();
      const tbody = document.getElementById('r-tbody');
      if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="9" style="color:#9ca3af;padding:14px">Zatím žádné poptávky.</td></tr>';
        return;
      }
      tbody.innerHTML = data.map((r, i) => {
        const stavCls = r.stav === 'potvrzeno' ? 'stav-potvrzeno' : r.stav === 'zruseno' ? 'stav-zruseno' : 'stav-cekajici';
        const stavLabel = r.stav === 'potvrzeno' ? 'Potvrzeno' : r.stav === 'zruseno' ? 'Zrušeno' : 'Čekající';
        // r.id je INTEGER PK z DB → bezpečné přes Number() (nemůže obsahovat HTML)
        const safeId = Number(r.id);
        const akceHtml = r.stav === 'zruseno' ? '—' :
          `<button class="btn-akce btn-potvrdit" onclick="rPotvrdit(${safeId})" ${r.stav==='potvrzeno'?'disabled':''}>Potvrdit</button>` +
          `<button class="btn-akce btn-zrusit" onclick="rZrusit(${safeId})">Zrušit</button>`;
        return `<tr>
          <td>${i+1}</td><td>${escapeHtml(r.pokoj)}</td><td>${escapeHtml(r.datum_od)}</td><td>${escapeHtml(r.datum_do)}</td>
          <td>${escapeHtml(r.jmeno)}</td><td>${escapeHtml(r.email)}</td><td>${r.telefon ? escapeHtml(r.telefon) : '—'}</td>
          <td><span class="stav-badge ${stavCls}">${stavLabel}</span></td>
          <td>${akceHtml}</td>
        </tr>`;
      }).join('');
    } catch(e) {
      document.getElementById('r-tbody').innerHTML = '<tr><td colspan="9" style="color:#991b1b">Chyba načítání.</td></tr>';
    }
  }

  async function rOdeslat() {
    const btn = document.getElementById('r-btn');
    const msg = document.getElementById('r-msg');
    msg.className = 'form-msg'; msg.textContent = '';
    const od = document.getElementById('r-od').value;
    const _do = document.getElementById('r-do').value;
    const jmeno = document.getElementById('r-jmeno').value.trim();
    const email = document.getElementById('r-email').value.trim();
    const tel = document.getElementById('r-telefon').value.trim();
    const pokoj = document.getElementById('r-pokoj').value;
    if (!od || !_do || !jmeno || !email) {
      msg.className = 'form-msg err'; msg.textContent = 'Vyplňte datum příjezdu, odjezdu, jméno a e-mail.'; return;
    }
    if (od >= _do) { msg.className = 'form-msg err'; msg.textContent = 'Datum odjezdu musí být po datu příjezdu.'; return; }
    btn.disabled = true; btn.textContent = 'Odesílám…';
    try {
      const res = await fetch(`/api/rezervace/${R_SLUG}`, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({jmeno, email, telefon: tel, pokoj, datum_od: od, datum_do: _do})
      });
      if (res.status === 409) { const e = await res.json(); msg.className='form-msg err'; msg.textContent=e.detail; return; }
      if (!res.ok) throw new Error();
      msg.className = 'form-msg ok'; msg.textContent = 'Poptávka odeslána! Termín bude potvrzen nebo zamítnut.';
      ['r-od','r-do','r-jmeno','r-email','r-telefon'].forEach(id => document.getElementById(id).value='');
      rNacist();
    } catch { msg.className='form-msg err'; msg.textContent='Chyba při odesílání. Zkuste to znovu.'; }
    finally { btn.disabled=false; btn.textContent='Odeslat poptávku'; }
  }

  async function rPotvrdit(id) {
    const res = await fetch(`/api/rezervace/${R_SLUG}/${id}/potvrdit`, {method:'PATCH'});
    if (res.status === 409) { alert('Termín koliduje s jinou potvrzenou rezervací.'); return; }
    rNacist();
  }

  async function rZrusit(id) {
    if (!confirm('Opravdu zrušit tuto rezervaci?')) return;
    await fetch(`/api/rezervace/${R_SLUG}/${id}/zrusit`, {method:'PATCH'});
    rNacist();
  }

  rNacist();

  // ── Blokace majitelem ────────────────────────────────────────────────────
  const R_TOKEN = new URLSearchParams(location.search).get('token') || '';
  if (R_TOKEN) document.getElementById('bl-panel').style.display = 'block';

  const fpBlOd = flatpickr('#bl-od', {
    locale: 'cs', dateFormat: 'Y-m-d', altInput: true, altFormat: 'd.m.Y',
    onChange: function(dates) { if (dates[0]) fpBlDo.set('minDate', dates[0]); }
  });
  const fpBlDo = flatpickr('#bl-do', {
    locale: 'cs', dateFormat: 'Y-m-d', altInput: true, altFormat: 'd.m.Y'
  });

  function blVseChange() {
    const vse = document.getElementById('bl-vse').checked;
    document.getElementById('bl-pokoj-wrap').style.opacity = vse ? '0.4' : '1';
    document.getElementById('bl-pokoj').disabled = vse;
  }

  async function blOdeslat() {
    const btn = document.getElementById('bl-btn');
    const msg = document.getElementById('bl-msg');
    msg.className = 'form-msg'; msg.textContent = '';
    const od = document.getElementById('bl-od').value;
    const _do = document.getElementById('bl-do').value;
    const vse = document.getElementById('bl-vse').checked;
    const pokoj = vse ? '*' : document.getElementById('bl-pokoj').value;
    if (!od || !_do) { msg.className = 'form-msg err'; msg.textContent = 'Vyplňte datum od a do.'; return; }
    if (od >= _do) { msg.className = 'form-msg err'; msg.textContent = 'Datum do musí být po datu od.'; return; }
    btn.disabled = true; btn.textContent = 'Blokuji…';
    try {
      const res = await fetch(`/api/rezervace/${R_SLUG}`, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ jmeno: 'Blokace', email: '', telefon: '', pokoj, datum_od: od, datum_do: _do, token: R_TOKEN })
      });
      if (!res.ok) throw new Error();
      msg.className = 'form-msg ok'; msg.textContent = 'Termín zablokován.';
      fpBlOd.clear(); fpBlDo.clear();
      document.getElementById('bl-vse').checked = false; blVseChange();
      rNacist();
    } catch { msg.className = 'form-msg err'; msg.textContent = 'Chyba. Zkontroluj token v URL.'; }
    finally { btn.disabled = false; btn.textContent = 'Zablokovat termín'; }
  }
</script>
```

## Krok 3 — Tracking notifikace mailem (Resend) — volitelné

Slouží k měření zájmu o rezervační formulář v preview kampaních (cold-outreach): když někdo vyplní formulář, dostaneš mail "engagement signal" a host dostane potvrzení z tvojí ověřené domény. V tracking/demo režimu jdou oba maily na **hardcoded adresy** — měníš je až když projekt přejde do produkce konkrétního klienta.

### Závislosti
```python
import os, requests, logging
logger = logging.getLogger(__name__)
```
A do `requirements.txt`: `requests` (pokud chybí).

### Env proměnné
```bash
RESEND_API_KEY=re_xxx...        # z resend.com/api-keys (Sending access, ne Full)
MAIL_FROM=Jméno <user@tvuj-domain.tld>   # MUSÍ být ověřená doména v Resend
PUBLIC_BASE_URL=https://tvuj-projekt.up.railway.app   # bez koncového /
```
Bez `RESEND_API_KEY` / `MAIL_FROM` běží `_send_email()` v **log-only** režimu — neodesílá, jen zapíše do logu. Vhodné pro lokál.

### Konstanty (přidat k ostatním na začátek souboru)
```python
# Tracking režim: všechna preview hlásí poptávky na tyhle 2 adresy.
# Až bude konkrétní klient, přidá se per-slug override (mapa slug → owner_email).
TRACKING_OWNER_EMAIL = "tvoje@adresa.cz"          # ← UPRAV
TRACKING_GUEST_EMAIL = "kontrolni-postschranka@gmail.com"  # ← UPRAV (vidíš co host dostává)
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "")
```

### Backend — helpery a notifikace (přidat za rezervační endpointy)
```python
RESEND_API_URL = "https://api.resend.com/emails"


def _send_email(to: str, subject: str, html: str, reply_to: str | None = None) -> bool:
    """Pošle 1 mail přes Resend. Bez env klíčů → log-only. Vrací True při úspěchu."""
    api_key = os.environ.get("RESEND_API_KEY")
    mail_from = os.environ.get("MAIL_FROM")
    if not api_key or not mail_from:
        logger.info("MAIL log-only → by-poslal komu=%s předmět=%s", to, subject)
        return False
    payload = {"from": mail_from, "to": [to], "subject": subject, "html": html}
    if reply_to:
        payload["reply_to"] = reply_to
    try:
        resp = requests.post(
            RESEND_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload, timeout=10,
        )
        if resp.status_code >= 400:
            logger.error("Resend chyba %s: %s", resp.status_code, resp.text[:300])
            return False
        return True
    except Exception as e:
        logger.error("Resend výjimka: %s", e)
        return False


def _detail_table_rows(data: RezervaciData) -> str:
    """Sdílená HTML tabulka detailů poptávky pro oba maily."""
    rows = [
        ("Pokoj", data.pokoj), ("Příjezd", data.datum_od), ("Odjezd", data.datum_do),
        ("Jméno", data.jmeno), ("E-mail", data.email), ("Telefon", data.telefon or "—"),
    ]
    return "".join(
        f'<tr><td style="padding:8px 14px;color:#6b7280;font-size:14px;border-bottom:1px solid #f0f0f0">{label}</td>'
        f'<td style="padding:8px 14px;color:#111827;font-size:14px;font-weight:600;border-bottom:1px solid #f0f0f0">{val}</td></tr>'
        for label, val in rows
    )


def _build_owner_email_html(slug: str, brand: str, data: RezervaciData) -> str:
    """Mail pro mě (tracking) — engagement signal že někdo vyplnil formulář v preview."""
    preview_url = f"{PUBLIC_BASE_URL}/preview/{slug}"
    return f"""\
<div style="font-family:-apple-system,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;background:#fff">
  <div style="background:#0f172a;padding:20px 28px">
    <div style="color:#22c55e;font-size:12px;letter-spacing:1.5px;font-weight:700">ENGAGEMENT SIGNAL</div>
    <div style="color:#fff;font-size:20px;font-weight:700;margin-top:4px">Nová poptávka v preview — {brand}</div>
  </div>
  <div style="padding:28px">
    <p style="color:#374151;font-size:15px;line-height:1.6;margin:0 0 20px">
      Někdo vyplnil rezervační formulář na preview <b>{slug}</b>. Reálný zájem — vhodný moment na follow-up.
    </p>
    <table style="width:100%;border-collapse:collapse;background:#fafafa;border-radius:8px;overflow:hidden;margin-bottom:24px">
      {_detail_table_rows(data)}
    </table>
    <a href="{preview_url}" style="display:inline-block;background:#0f172a;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">
      Otevřít preview →
    </a>
    <p style="color:#6b7280;font-size:13px;line-height:1.5;margin:24px 0 0">
      Když odpovíte, píšete přímo hostovi (<b>{data.email}</b>) — Reply-To je nastaveno.
    </p>
  </div>
  <div style="background:#f9fafb;padding:16px 28px;color:#9ca3af;font-size:12px;text-align:center">
    Tracking notifikace · slug <code>{slug}</code>
  </div>
</div>"""


def _build_guest_email_html(brand: str, data: RezervaciData) -> str:
    """Mail pro hosta — potvrzení (vypadá jako od reálného ubytování). Zelený branding."""
    return f"""\
<div style="font-family:-apple-system,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;background:#fff">
  <div style="background:#2d5a27;padding:32px 28px;text-align:center">
    <div style="color:#fff;font-size:24px;font-weight:700;font-family:Georgia,serif">{brand}</div>
    <div style="color:rgba(255,255,255,0.8);font-size:13px;margin-top:6px">Potvrzení poptávky rezervace</div>
  </div>
  <div style="padding:28px">
    <p style="color:#111827;font-size:16px;line-height:1.6;margin:0 0 16px">Dobrý den {data.jmeno},</p>
    <p style="color:#374151;font-size:15px;line-height:1.6;margin:0 0 20px">
      přijali jsme vaši poptávku ubytování. Termín a dostupnost pokoje vám potvrdíme
      <b>do 24 hodin</b> e-mailem nebo telefonicky.
    </p>
    <div style="background:#f0f7ee;border-left:3px solid #2d5a27;padding:14px 18px;margin-bottom:20px;border-radius:4px">
      <div style="color:#2d5a27;font-size:12px;font-weight:700;letter-spacing:1px;margin-bottom:8px">SHRNUTÍ POPTÁVKY</div>
      <table style="width:100%;border-collapse:collapse">
        {_detail_table_rows(data)}
      </table>
    </div>
    <p style="color:#6b7280;font-size:14px;line-height:1.6;margin:0 0 16px">
      Pokud máte mezitím dotaz, odpovězte na tento e-mail.
    </p>
    <p style="color:#111827;font-size:15px;margin:24px 0 0">
      S pozdravem,<br><b>{brand}</b>
    </p>
  </div>
  <div style="background:#f9fafb;padding:16px 28px;color:#9ca3af;font-size:12px;text-align:center">
    Tento e-mail je automatické potvrzení vaší poptávky.
  </div>
</div>"""


def _notify_new_rezervace(slug: str, data: RezervaciData):
    """Tracking režim: pošle 2 maily na hardcoded adresy.
      1) TRACKING_OWNER_EMAIL — engagement signal (Reply-To = host pro přímou odpověď)
      2) TRACKING_GUEST_EMAIL — kopie potvrzení co by host dostal (kontrola UX)
    `brand` načti z preview names mapy (slug → název projektu) nebo fallback na "ubytování".
    Selhání odeslání NIKDY neshodí uložení rezervace — voláno v try/except v endpointu."""
    brand = _load_preview_names().get(slug) or "ubytování"  # ← použij vlastní brand resolver
    _send_email(
        to=TRACKING_OWNER_EMAIL,
        subject=f"[Preview] {brand} — zájem o rezervaci ({data.datum_od} → {data.datum_do})",
        html=_build_owner_email_html(slug, brand, data),
        reply_to=data.email,
    )
    _send_email(
        to=TRACKING_GUEST_EMAIL,
        subject=f"Potvrzení poptávky – {brand}",
        html=_build_guest_email_html(brand, data),
    )
```

### Zavolat z `create_rezervace` (Krok 1) — po `INSERT`, mimo `with` blok
```python
# ... INSERT ...
try:
    _notify_new_rezervace(slug, data)
except Exception as e:
    logger.error("Notifikace rezervace selhala: %s", e)
return {"ok": True}
```
**Mimo `with` blok** = rezervace je už commitnutá v DB; mailové selhání nesmí shodit uložený záznam.

### Rate limit (doporučeno když posíláš maily)
Hardcoded tracking maily jsou snadný cíl bot-spamu (vyčerpají Resend kvótu). Přidej `slowapi`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/rezervace/{slug}")
@limiter.limit("5/minute;30/hour")
def create_rezervace(request: Request, slug: str, data: RezervaciData):  # request: Request je povinný
    ...
```
Burst 5 stačí na překlepy/double-submit, 30/h zastaví scrapery dřív než vyčerpají kvótu.

### DNS setup (jednorázově při zakládání domény v Resend)
Resend ti při přidání domény vygeneruje 3 záznamy — všechny musí být zelené:
1. **DKIM** — `TXT  resend._domainkey  →  p=MII...` (Resend ti dá konkrétní hodnotu)
2. **SPF** — `TXT  send  →  v=spf1 include:amazonses.com ~all` (subdoména `send`, ne root)
3. **MX** — `MX   send  →  feedback-smtp.eu-west-1.amazonses.com` priorita 10

**Pasti:**
- Některé DNS panely (Forpsi) neumí MX na subdoméně přes form — migruj na Cloudflare ("DNS only" / gray cloud, ne proxied).
- Cloudflare Proxy (oranžový mrak) **rozbije Railway custom doménu** → vždy "DNS only" pro A/AAAA/CNAME mířící na Railway.
- DNSSEC u staré domény blokuje výměnu nameserverů → vypnout v parent registrátorovi, počkat 30–60 min na propagaci (`dig +short DS tvuj-domain.cz @8.8.8.8` musí být prázdné), pak teprve měnit NS.
- Sending access klíče (ne Full access) — princip minimálních oprávnění.

### Lokální test bez Resend
1. Nech `RESEND_API_KEY` / `MAIL_FROM` nevyplněné v `.env`
2. Vyplň formulář v preview → v logu se objeví `MAIL log-only → by-poslal komu=... předmět=...`
3. Tím ověříš že volání endpointu funguje, branding mailů ladíš přes `_build_*_email_html()` v jednorázovém skriptu (zapiš HTML do `tmp/mail_*.html` a otevři v browseru)

---

## Použití v novém projektu (checklist)
1. Zkopíruj endpointy do `server.py` (přidej `RESERVATIONS_DB` a `from pydantic import BaseModel`)
2. Vlož HTML blok do preview souboru / šablony
3. Nahraď `NAZEV_SLUG` slugem projektu
4. Nahraď seznam pokojů na **dvou místech**: v `<select id="r-pokoj">` (host) a `<select id="bl-pokoj">` (majitel)
5. Uprav barvy/CSS proměnné podle design systému projektu
6. Nastav `OWNER_TOKEN` env proměnnou (libovolný tajný řetězec)
7. Majiteli předej URL ve tvaru `https://domena.cz/stránka?token=OWNER_TOKEN` — owner form se zobrazí automaticky
8. **Volitelně tracking maily (Krok 3):** ověř doménu v Resend (DKIM/SPF/MX), přidej `RESEND_API_KEY`/`MAIL_FROM`/`PUBLIC_BASE_URL` env, uprav `TRACKING_OWNER_EMAIL`/`TRACKING_GUEST_EMAIL` konstanty, přidej rate limit, zavolej `_notify_new_rezervace()` z `create_rezervace`

> **Pro produkci doporučuji přidat plnohodnotný admin login** podle [ADMIN_AUTH.md](./ADMIN_AUTH.md) — `OWNER_TOKEN` v URL je vhodný jen pro preview/demo (token leak-uje přes Referer, historii prohlížeče, atd.).

## Možné duplicity v hostujícím projektu — zkontrolovat před aplikací skillu

Skill kopíruje hotové funkce do `server.py`. Pokud projekt už podobné věci má (typicky pokud běží i `sent.db` / `lead_state` pro cold mailing), vznikne duplicita. Před vložením zkontroluj:

- **`_ensure_rezervace_schema()`** — projekt nejspíš má `_ensure_state_schema()` (pro `lead_state` v `sent.db`). Vzorec `PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS ...` je identický. Pokud refaktoruješ, sjednoť do `db.py` se společným `init_all_schemas()`.
- **`RESERVATIONS_DB` cesta** — pokud projekt už definuje `SENT_DB = BASE_DIR / "data" / "sent.db"` se stejným podmíněným Railway přepínačem (`Path("/data/...")` vs `BASE_DIR / "data" / "..."`), použij stejný vzorec, ať se cesty drží na jednom místě (`config.py`).
- **`slug` parametry v endpointech** — pokud projekt už má slug funkce (`_row_slug`, `slug_from_preview_url`, `_web_slug`), nezduplikuj logiku v rezervačních endpointech. Použij existující helper.
- **DB connection pattern** — `with sqlite3.connect(str(RESERVATIONS_DB)) as conn:` se opakuje v každém endpointu. Pokud projekt už má connection helper (context manager), použij ho. Pokud ne, refaktor je dobrá příležitost ho vytvořit.
- **`datetime.now(timezone.utc).isoformat()`** — pokud projekt má helper `_now_utc_iso()` (pravděpodobně v `dashboard.py` nebo `server.py`), použij ho místo opakování inline.
- **Pydantic modely** — pokud projekt už má `LeadData` / podobné modely, drž se stejné konvence pojmenování polí (snake_case, anglické názvy) místo míchání `jmeno` vs `name`.
- **Pokud projekt používá souběžně i `rezervacni-system-lekari`** — sdílej `RESERVATIONS_DB` cestu (tabulky `rezervace` a `doctor_booking` v jedné DB jsou OK) a stejnou `_ensure_*_schema()` konvenci.

