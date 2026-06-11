# Skill: Rezervační systém pro hotel/ubytování

Přidá funkční rezervační systém do projektu s FastAPI backendem a HTML preview stránkou.

## Co systém umí
- Formulář s výběrem pokoje, termínu (Flatpickr kalendář), jména, emailu, telefonu
- Potvrzené termíny jsou vizuálně blokovány v kalendáři (červeně, nelze vybrat)
- Různé pokoje lze rezervovat na stejný termín nezávisle
- Admin tabulka s tlačítky Potvrdit / Zrušit
- Po potvrzení se termín zablokuje pro ostatní hosty
- SQLite databáze, WAL mode

---

## Krok 1 — Přidej do server.py

### Závislosti (přidat k importům pokud chybí)
```python
from pydantic import BaseModel
```

### Cesta k DB (přidat k ostatním DB cestám)
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
    pokoj: str
    datum_od: str   # formát YYYY-MM-DD
    datum_do: str   # formát YYYY-MM-DD


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
    RESERVATIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        konflikt = conn.execute("""
            SELECT id FROM rezervace
            WHERE slug = ? AND pokoj = ? AND stav = 'potvrzeno'
              AND datum_od < ? AND datum_do > ?
        """, (slug, data.pokoj, data.datum_do, data.datum_od)).fetchone()
        if konflikt:
            raise HTTPException(status_code=409, detail="Termín je již obsazen pro tento pokoj.")
        conn.execute("""
            INSERT INTO rezervace (slug, jmeno, email, telefon, pokoj, datum_od, datum_do, stav, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'cekajici', ?)
        """, (
            slug, data.jmeno, data.email, data.telefon,
            data.pokoj, data.datum_od, data.datum_do,
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

---

## Krok 2 — Přidej do HTML preview souboru

Vlož před sekci s kontaktem/poptávkou (`<section id="rezervace"...>`).

Nahraď `NAZEV_SLUG` skutečným slugem projektu (např. `novahospoda-eu`).
Nahraď seznam pokojů skutečnými typy pokojů klienta.

```html
<!-- ─── FLATPICKR ─── -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/cs.js"></script>
<style>
  .flatpickr-day.disabled, .flatpickr-day.disabled:hover {
    background: #fee2e2 !important; color: #ef4444 !important;
    text-decoration: line-through; cursor: not-allowed !important;
  }
</style>

<!-- ─── REZERVAČNÍ SYSTÉM ─── -->
<style>
  .rezervace-section { max-width: 960px; margin: 60px auto 0; padding: 0 24px; }
  .rezervace-section h2 { font-family: 'Playfair Display', serif; font-size: 2rem; color: var(--green); margin-bottom: 8px; }
  .rezervace-section .subtitle { color: var(--text-muted); margin-bottom: 32px; font-size: 0.95rem; }
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
    return vsechnyRezervace
      .filter(r => r.stav === 'potvrzeno' && r.pokoj === pokoj)
      .map(r => ({ from: r.datum_od, to: r.datum_do }));
  }

  function aktualizovatKalendar() {
    const pokoj = document.getElementById('r-pokoj').value;
    const obsazene = ziskatObsazene(pokoj);
    fpOd.set('disable', obsazene); fpDo.set('disable', obsazene);
    fpOd.clear(); fpDo.clear();
  }

  document.getElementById('r-pokoj').addEventListener('change', aktualizovatKalendar);

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
        const akceHtml = r.stav === 'zruseno' ? '—' :
          `<button class="btn-akce btn-potvrdit" onclick="rPotvrdit(${r.id})" ${r.stav==='potvrzeno'?'disabled':''}>Potvrdit</button>` +
          `<button class="btn-akce btn-zrusit" onclick="rZrusit(${r.id})">Zrušit</button>`;
        return `<tr>
          <td>${i+1}</td><td>${r.pokoj}</td><td>${r.datum_od}</td><td>${r.datum_do}</td>
          <td>${r.jmeno}</td><td>${r.email}</td><td>${r.telefon||'—'}</td>
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
</script>
```

---

## Použití v novém projektu

1. Zkopíruj endpointy do `server.py` (přidej `RESERVATIONS_DB` cestu a `from pydantic import BaseModel`)
2. Vlož HTML blok do preview souboru před sekci s kontaktem
3. Nahraď `NAZEV_SLUG` slugem projektu
4. Nahraď seznam pokojů skutečnými typy pokojů klienta
5. CSS proměnné (`--green`, `--cream` atd.) musí existovat v projektu — případně nahraď konkrétními barvami
