---
name: rezervacni-system-lekari
description: Přidá rezervační systém pro lékaře (FastAPI + SQLite + vanilla JS injektovaný do SSR HTML) — booking formulář s klikacími sloty, admin přehled s Potvrdit/Zrušit, blokování víkendů a obsazených termínů. Určeno pro statické SSR preview stránky bez React hydratace.
---

# Rezervační systém — lékař (FastAPI + SQLite + injektovaný JS)

Systém pro objednávání pacientů k lékaři. Funguje jako standalone vanilla JS skript injektovaný do statického SSR HTML — žádná závislost na Reactu ani TanStack Routeru.

## Co systém umí
- Formulář v existující React SSR sekci (datum, jméno, telefon, email)
- Výběr času jako **klikatelné tagy** (8:00–17:30, každých 30 min) — zobrazí se až po výběru data
- Po výběru data: fetch obsazených slotů → obsazené přeškrtnuté a disabled
- **Víkendy automaticky zablokované** — všechny sloty disabled pro sobotu/neděli
- Nový termín se ukládá jako `cekajici` (čeká na potvrzení lékařem)
- **Potvrdit** jen pro stav `cekajici` (ne pro `zruseno`)
- **Zrušit** pro vše kromě `zruseno`
- Admin tabulka: Datum (dd.mm.rrrr), Čas, Jméno, Telefon, Email, Stav, Akce
- Demo data při prvním zobrazení — stav `demo`, **neblokují** sloty pro reálné pacienty
- Disabled placeholder sekce "Nejsem k dispozici" (příprava pro správu dostupnosti)
- SQLite databáze, WAL mode

## TODO — chybějící funkce

- [ ] **Ordinační hodiny:** každý lékař má různé dny a hodiny provozu — sloty 8:00–17:30 to ignorují.
  - **Zvolený přístup (Návrh B rozšířený o per-den granularitu):**
  - `doctor.json` dostane pole `ordinacni_hodiny` — per-den rozsah jako `{"1": ["08:00","12:00"], "3": ["13:00","17:00"], "0": null, ...}` (klíče = `getDay()`, `null` = zavřeno)
  - Backend: endpoint `/api/booking/{slug}/slots` rozšíří odpověď z `["09:00"]` na `{"taken": ["09:00"], "range": ["08:00","12:00"]}` — range čte z `doctor.json[den]`
  - Frontend JS (`preview.py`): zobrazit jen sloty v `range`, přeškrtnout `taken`; pokud `range = null` → disabled všechny sloty + zpráva "Ordinace v tento den není"
  - Zavřené dny blokovat i server-side (`range: null`) — nestačí jen vizuálně v date inputu

- [ ] **Stav "obslouženo":** označení pacienta jako obslouženého bez mazání záznamu z DB
  - Přidat stav `obslouženo` vedle `cekajici`, `potvrzeno`, `zruseno`
  - Tlačítko "Obslouženo" v admin tabulce — jen pro stav `potvrzeno`
  - Backend: endpoint `/api/booking/{slug}/{id}/obsloužit` → UPDATE stav = 'obslouženo'
  - Výchozí filtr tabulky: skrýt `obslouženo` starší než dnešní datum, zobrazit jen aktivní
  - Zachovat historii — nikdy nemaž záznamy z DB (statistiky, oprava chyby)

- [ ] **Notifikace po objednání — email nebo SMS pacientovi:**
  - Email: po úspěšném POST `/api/booking/{slug}` odeslat pacientovi potvrzovací email s datem, časem a kontaktem ordinace (SMTP přes `smtplib` nebo SendGrid API)
  - SMS: alternativa přes Twilio nebo Vonage API — jednodušší pro pacienta, nevyžaduje email
  - Konfigurace v `doctor.json`: `notifikace: "email"` / `"sms"` / `null` — lékař si zvolí
  - Lékař dostane kopii notifikace (nebo jen interní záznam v DB)
  - Preferovaný způsob: email (bez externích závislostí pokud SMTP k dispozici)

- [ ] **Stránkování admin tabulky:** max 50 záznamů na stránce, číslované stránky
  - Backend: endpoint `/api/booking/{slug}` dostane query param `page` (default 1) a vrátí `{"rows": [...], "total": 123, "page": 1, "pages": 3}`
  - Frontend JS: pod tabulkou vykreslit čísla stránek `« 1 2 3 »`, aktivní stránka zvýrazněna
  - Při přepnutí stránky nový fetch, ne reload celé stránky

## Architektura — klíčový rozdíl od ubytování

Booking systém pro lékaře **nevkládá novou HTML sekci** — napojuje se na existující sekce vyrenderované React SSR šablonou:
- `form.sm\:col-span-2` — formulář pro objednání (React renderoval se `disabled` tlačítkem a bez time inputu)
- `.mt-14.rounded-3xl` — kontejner admin přehledu (React renderoval "Načítám…" placeholder)

Po `strip_js()` (odebrání všech `<script>` tagů ze SSR HTML) se tento skript injektuje před `</body>` a přebírá obě sekce.

## Předpoklady
- FastAPI aplikace s `src/server.py`
- `RESERVATIONS_DB` cesta k SQLite souboru (`data/reservations.db` lokálně, `/data/reservations.db` na Railway)
- SSR HTML šablona s `form.sm\:col-span-2` formulářem a `.mt-14.rounded-3xl` admin sekcí (gynekologie template)
- Bun + `template/ssr-render.js` pro SSR generování

## Krok 1 — Backend (FastAPI)

### Pydantic model a schema

```python
# ─── DOCTOR BOOKING ──────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    jmeno: str
    telefon: str
    email: str
    datum: str   # YYYY-MM-DD
    cas: str     # HH:MM


def _ensure_booking_schema(conn: sqlite3.Connection):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctor_booking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL,
            jmeno TEXT NOT NULL,
            telefon TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            datum TEXT NOT NULL,
            cas TEXT NOT NULL,
            stav TEXT NOT NULL DEFAULT 'cekajici',
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_booking_slug ON doctor_booking(slug)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_booking_datum ON doctor_booking(datum)")
```

### Demo data — stav `demo` (neblokuje sloty)

```python
def _seed_demo_booking(conn: sqlite3.Connection, slug: str):
    """Vloží ukázkové termíny při prvním dotazu. stav='demo' → neblokují reálné sloty."""
    from datetime import date, timedelta
    today = date.today()
    now = datetime.now(timezone.utc).isoformat()
    demo = [
        {"jmeno": "Jana Horáková",     "telefon": "+420 731 111 222", "email": "jana.horakova@email.cz",   "datum": (today + timedelta(days=5)).isoformat(), "cas": "09:00", "stav": "demo"},
        {"jmeno": "Martina Svobodová", "telefon": "+420 604 333 444", "email": "m.svobodova@seznam.cz",     "datum": (today + timedelta(days=5)).isoformat(), "cas": "10:30", "stav": "demo"},
        {"jmeno": "Petra Nováčková",   "telefon": "",                 "email": "petra.novackova@gmail.com", "datum": (today + timedelta(days=6)).isoformat(), "cas": "08:30", "stav": "demo"},
        {"jmeno": "Lucie Dvořáková",   "telefon": "+420 776 555 666", "email": "lucie.dvorakova@gmail.com", "datum": (today + timedelta(days=6)).isoformat(), "cas": "14:00", "stav": "demo"},
        {"jmeno": "Tereza Marková",    "telefon": "+420 602 777 888", "email": "tereza.markova@email.cz",  "datum": (today + timedelta(days=7)).isoformat(), "cas": "11:00", "stav": "demo"},
    ]
    for r in demo:
        conn.execute("""
            INSERT INTO doctor_booking (slug, jmeno, telefon, email, datum, cas, stav, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (slug, r["jmeno"], r["telefon"], r["email"], r["datum"], r["cas"], r["stav"], now))
```

### Endpointy

```python
@app.get("/api/booking/{slug}/slots")
def booking_slots(slug: str, datum: str):
    """Vrátí seznam obsazených časů (HH:MM) pro daný den. Ignoruje stav 'demo'."""
    RESERVATIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_booking_schema(conn)
        rows = conn.execute("""
            SELECT cas FROM doctor_booking
            WHERE slug = ? AND datum = ? AND stav NOT IN ('zruseno', 'demo')
        """, (slug, datum)).fetchall()
    return [r[0] for r in rows]


@app.post("/api/booking/{slug}")
def create_booking(slug: str, data: BookingCreate):
    """Vytvoří nový termín (stav = cekajici). Konflikt ignoruje 'demo' záznamy."""
    RESERVATIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_booking_schema(conn)
        existing = conn.execute("""
            SELECT id FROM doctor_booking
            WHERE slug = ? AND datum = ? AND cas = ? AND stav NOT IN ('zruseno', 'demo')
        """, (slug, data.datum, data.cas)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Tento termín je již obsazen.")
        conn.execute("""
            INSERT INTO doctor_booking (slug, jmeno, telefon, email, datum, cas, stav, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'cekajici', ?)
        """, (slug, data.jmeno, data.telefon, data.email, data.datum, data.cas,
              datetime.now(timezone.utc).isoformat()))
    return {"ok": True}


@app.get("/api/booking/{slug}")
def get_booking_rezervace(slug: str):
    """Vrátí všechny termíny pro daný slug (admin přehled). Při prvním dotazu vloží demo data."""
    RESERVATIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_booking_schema(conn)
        count = conn.execute(
            "SELECT COUNT(*) FROM doctor_booking WHERE slug = ?", (slug,)
        ).fetchone()[0]
        if count == 0:
            _seed_demo_booking(conn, slug)
        rows = conn.execute("""
            SELECT id, jmeno, telefon, email, datum, cas, stav, created_at
            FROM doctor_booking WHERE slug = ?
            ORDER BY datum ASC, cas ASC
        """, (slug,)).fetchall()
    return JSONResponse([{
        "id": r[0], "jmeno": r[1], "telefon": r[2], "email": r[3],
        "datum": r[4], "cas": r[5], "stav": r[6], "created_at": r[7]
    } for r in rows])


@app.post("/api/booking/{slug}/{rezervace_id}/potvrdit")
def potvrdit_booking(slug: str, rezervace_id: int):
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_booking_schema(conn)
        conn.execute(
            "UPDATE doctor_booking SET stav = 'potvrzeno' WHERE id = ? AND slug = ?",
            (rezervace_id, slug)
        )
    return {"ok": True}


@app.post("/api/booking/{slug}/{rezervace_id}/zrusit")
def zrusit_booking(slug: str, rezervace_id: int):
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_booking_schema(conn)
        conn.execute(
            "UPDATE doctor_booking SET stav = 'zruseno' WHERE id = ? AND slug = ?",
            (rezervace_id, slug)
        )
    return {"ok": True}
```

## Krok 2 — Injektovaný JS skript

```python
_BOOKING_SCRIPT = r"""
<script>
(function () {
  'use strict';
  var SLUG = '{{SLUG}}';

  /* ── Stylování ──────────────────────────────────────────────────── */
  var STYLE = document.createElement('style');
  STYLE.textContent = [
    '.bk-table{width:100%;border-collapse:collapse;font-size:13px}',
    '.bk-table th{background:#f8f8f8;padding:8px 12px;text-align:left;font-weight:600;border-bottom:1px solid #e5e7eb;white-space:nowrap}',
    '.bk-table td{padding:8px 12px;border-bottom:1px solid #f3f4f6;vertical-align:middle}',
    '.bk-table tr:last-child td{border-bottom:none}',
    '.bk-badge{display:inline-block;padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:600;white-space:nowrap}',
    '.bk-btn{padding:4px 10px;border-radius:6px;font-size:12px;cursor:pointer;border:1px solid transparent;font-weight:500;margin-right:4px}',
    '.bk-btn-ok{background:#dcfce7;color:#166534;border-color:#bbf7d0}',
    '.bk-btn-ok:hover{background:#bbf7d0}',
    '.bk-btn-cancel{background:#fee2e2;color:#991b1b;border-color:#fecaca}',
    '.bk-btn-cancel:hover{background:#fecaca}',
    '.bk-msg{padding:12px 24px;font-size:13px}',
    '.bk-ok{color:#166534;padding:8px 24px;font-size:13px}',
    '.bk-err{color:#dc2626;padding:8px 24px;font-size:13px}',
  ].join('');
  document.head.appendChild(STYLE);

  /* ── 1) Booking formulář (Objednat se online) ───────────────────── */
  var form = document.querySelector('form.sm\:col-span-2');
  if (form) {
    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.removeAttribute('disabled');

    /* Tagy pro výběr času — skryté dokud pacient nevybere datum */
    var selectedCas = '';
    var timeWrap = document.createElement('div');
    timeWrap.className = 'flex-col gap-1.5';
    timeWrap.style.display = 'none';
    var slots = [];
    for (var h = 8; h < 18; h++) {
      ['00','30'].forEach(function(m) {
        slots.push((h < 10 ? '0' : '') + h + ':' + m);
      });
    }
    var slotsHtml = slots.map(function(val) {
      return '<button type="button" data-cas="' + val + '" ' +
        'class="bk-slot rounded-lg px-3 py-1.5 text-sm border transition-colors bg-background border-border/60 hover:border-primary hover:text-primary">' +
        val + '</button>';
    }).join('');
    timeWrap.innerHTML = '<label class="text-xs font-medium text-foreground/70">Vyberte čas *</label>' +
      '<div class="flex flex-wrap gap-2 mt-1">' + slotsHtml + '</div>';
    var dateWrap = form.querySelector('div.flex.flex-col.gap-1\.5');
    if (dateWrap && dateWrap.parentNode) dateWrap.after(timeWrap);
    else form.insertBefore(timeWrap, submitBtn ? submitBtn.parentNode : null);

    /* Klik na slot (jen enabled) */
    function bindSlotClicks() {
      timeWrap.querySelectorAll('.bk-slot:not([disabled])').forEach(function(btn) {
        btn.onclick = function() {
          timeWrap.querySelectorAll('.bk-slot').forEach(function(b) {
            if (!b.disabled) b.className = 'bk-slot rounded-lg px-3 py-1.5 text-sm border transition-colors bg-background border-border/60 hover:border-primary hover:text-primary';
          });
          btn.className = 'bk-slot rounded-lg px-3 py-1.5 text-sm border transition-colors bg-primary text-primary-foreground border-primary';
          selectedCas = btn.getAttribute('data-cas');
        };
      });
    }
    bindSlotClicks();

    /* Při změně data: zobraz tagy, zablokuj víkend / obsazené sloty */
    var dateInput = form.querySelector('input[type="date"]');
    if (dateInput) {
      dateInput.addEventListener('change', function() {
        selectedCas = '';
        timeWrap.style.display = dateInput.value ? 'flex' : 'none';
        timeWrap.querySelectorAll('.bk-slot').forEach(function(b) {
          b.disabled = false;
          b.className = 'bk-slot rounded-lg px-3 py-1.5 text-sm border transition-colors bg-background border-border/60 hover:border-primary hover:text-primary';
        });
        if (!dateInput.value) return;
        /* Víkendy — zablokuj všechny sloty */
        var den = new Date(dateInput.value).getDay();
        if (den === 0 || den === 6) {
          timeWrap.querySelectorAll('.bk-slot').forEach(function(b) {
            b.disabled = true;
            b.className = 'bk-slot rounded-lg px-3 py-1.5 text-sm border line-through opacity-40 cursor-not-allowed bg-muted border-border/30';
          });
          return;
        }
        /* Obsazené sloty z API */
        fetch('/api/booking/' + SLUG + '/slots?datum=' + dateInput.value)
          .then(function(r) { return r.json(); })
          .then(function(taken) {
            timeWrap.querySelectorAll('.bk-slot').forEach(function(b) {
              if (taken.indexOf(b.getAttribute('data-cas')) !== -1) {
                b.disabled = true;
                b.className = 'bk-slot rounded-lg px-3 py-1.5 text-sm border line-through opacity-40 cursor-not-allowed bg-muted border-border/30';
              }
            });
          });
      });
    }

    /* Zpráva pod tlačítkem */
    var msgEl = document.createElement('span');
    msgEl.style.fontSize = '13px';
    if (submitBtn && submitBtn.parentNode) submitBtn.parentNode.appendChild(msgEl);

    /* Disabled placeholder: Nejsem k dispozici + Úprava ordinačních hodin */
    var unavailWrap = document.createElement('div');
    unavailWrap.style.cssText = 'margin-top:16px;padding-top:16px;border-top:1px solid #e5e7eb;display:flex;flex-direction:column;gap:8px;opacity:0.5;pointer-events:none';
    unavailWrap.innerHTML =
      '<div style="display:flex;align-items:center;gap:10px">' +
        '<button disabled style="padding:8px 16px;background:#ef4444;color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:500;cursor:not-allowed">Nejsem k dispozici</button>' +
        '<label style="display:flex;align-items:center;gap:6px;font-size:13px;color:#374151;cursor:not-allowed">' +
          '<input type="checkbox" disabled> celý den' +
        '</label>' +
      '</div>' +
      '<span class="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-3 py-1 whitespace-nowrap">Úprava ordinačních hodin, nastavení dovolené</span>';
    if (submitBtn && submitBtn.parentNode) submitBtn.parentNode.appendChild(unavailWrap);

    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var inputs = form.querySelectorAll('input');
      var datum = '', jmeno = '', telefon = '', email = '';
      inputs.forEach(function(inp) {
        if (inp.type === 'date')  datum   = inp.value;
        if (inp.type === 'text')  jmeno   = inp.value;
        if (inp.type === 'tel')   telefon = inp.value;
        if (inp.type === 'email') email   = inp.value;
      });
      var cas = selectedCas;
      if (!datum || !jmeno || !cas) {
        msgEl.textContent = 'Vyplňte všechna povinná pole.';
        msgEl.className = 'bk-err';
        return;
      }
      submitBtn.disabled = true;
      msgEl.textContent = 'Ukládám…';
      msgEl.className = '';
      fetch('/api/booking/' + SLUG, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({jmeno: jmeno, telefon: telefon, email: email, datum: datum, cas: cas})
      })
      .then(function(r) {
        if (!r.ok) return r.json().then(function(d) { throw new Error(d.detail || 'Chyba'); });
        return r.json();
      })
      .then(function() {
        msgEl.textContent = '✓ Termín uložen';
        msgEl.className = 'bk-ok';
        form.reset();
        selectedCas = '';
        timeWrap.style.display = 'none';
        timeWrap.querySelectorAll('.bk-slot').forEach(function(b) {
          b.disabled = false;
          b.className = 'bk-slot rounded-lg px-3 py-1.5 text-sm border transition-colors bg-background border-border/60 hover:border-primary hover:text-primary';
        });
        submitBtn.disabled = false;
        load();
      })
      .catch(function(err) {
        msgEl.textContent = '✗ ' + (err.message || 'Chyba uložení');
        msgEl.className = 'bk-err';
        submitBtn.disabled = false;
      });
    });
  }

  /* ── 2) Tabulka rezervací (Přehled rezervací) ───────────────────── */
  var container = document.querySelector('.mt-14.rounded-3xl');
  if (!container) return;

  var loadingEl = container.querySelector('p.px-6.py-4');
  if (!loadingEl) return;

  var wrap = document.createElement('div');
  loadingEl.replaceWith(wrap);

  var refreshBtn = container.querySelector('button');
  if (refreshBtn) refreshBtn.addEventListener('click', load);

  function fmtDatum(d) {
    var p = (d || '').split('-');
    return p.length === 3 ? p[2] + '.' + p[1] + '.' + p[0] : d;
  }

  function stav(s) {
    var map = {potvrzeno:'#166534:#dcfce7',zruseno:'#991b1b:#fee2e2',cekajici:'#b45309:#fef3c7',demo:'#6b7280:#f3f4f6'};
    var c = (map[s] || '#374151:#f3f4f6').split(':');
    return '<span class="bk-badge" style="color:' + c[0] + ';background:' + c[1] + '">' + s + '</span>';
  }

  function render(rows) {
    if (!rows.length) {
      wrap.innerHTML = '<p class="bk-msg" style="color:#6b7280">Žádné rezervace</p>';
      return;
    }
    var html = '<div style="overflow-x:auto"><table class="bk-table"><thead><tr>' +
      '<th>Datum</th><th>Čas</th><th>Jméno</th><th>Telefon</th><th>Email</th><th>Stav</th><th>Akce</th>' +
      '</tr></thead><tbody>';
    rows.forEach(function(r) {
      var akce = '';
      if (r.stav === 'cekajici') akce += '<button class="bk-btn bk-btn-ok" data-id="' + r.id + '" data-action="potvrdit">Potvrdit</button>';
      if (r.stav !== 'zruseno')  akce += '<button class="bk-btn bk-btn-cancel" data-id="' + r.id + '" data-action="zrusit">Zrušit</button>';
      html += '<tr><td>' + fmtDatum(r.datum) + '</td><td>' + r.cas + '</td><td><strong>' + (r.jmeno||'') +
        '</strong></td><td>' + (r.telefon||'—') + '</td><td>' + (r.email||'—') +
        '</td><td>' + stav(r.stav) + '</td><td>' + akce + '</td></tr>';
    });
    html += '</tbody></table></div>';
    wrap.innerHTML = html;
    wrap.querySelectorAll('[data-action]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        fetch('/api/booking/' + SLUG + '/' + btn.getAttribute('data-id') + '/' + btn.getAttribute('data-action'),
          {method:'POST'}).then(function() { load(); });
      });
    });
  }

  function load() {
    wrap.innerHTML = '<p class="bk-msg" style="color:#9ca3af">Načítám…</p>';
    fetch('/api/booking/' + SLUG)
      .then(function(r) { return r.json(); })
      .then(render)
      .catch(function() {
        wrap.innerHTML = '<p class="bk-msg" style="color:#dc2626">Chyba načítání rezervací.</p>';
      });
  }

  load();
})();
</script>
"""


def _inject_booking_script(html: str, slug: str) -> str:
    """Injektuje standalone booking script před </body> (jen pro hlavní stránku)."""
    script = _BOOKING_SCRIPT.replace("{{SLUG}}", slug)
    return html.replace("</body>", script + "</body>", 1)
```

### Volání v pipeline generování HTML

```python
html = _html_strip_js(html)        # odstraní všechny <script> a modulepreload linky
html = _html_rewrite_links(html, slug)
html = _html_rewrite_assets(html)
if ssr_path == "/":                # booking sekce jen na hlavní stránce, ne /cenik
    html = _inject_booking_script(html, slug)
```

## Použití v novém projektu (checklist)
1. Zkopíruj backend sekci do `server.py` (model, schema, seed, endpointy)
2. Přidej `_BOOKING_SCRIPT` konstantu a `_inject_booking_script` funkci
3. Zavolej `_inject_booking_script` v pipeline generování HTML (jen pro `ssr_path == "/"`)
4. Ověř CSS selektory šablony: `form.sm\:col-span-2` a `.mt-14.rounded-3xl` — pokud se šablona změní, tyto selektory je nutné aktualizovat
5. Na Railway: nastav Volume `/data` pro SQLite persistence

## Možné duplicity v hostujícím projektu — zkontrolovat před aplikací skillu

Skill kopíruje hotové funkce do `server.py`. Pokud projekt už podobné věci má (typicky pokud běží i `sent.db` / `lead_state` pro cold mailing), vznikne duplicita. Před vložením zkontroluj:

- **`_ensure_booking_schema()`** — projekt nejspíš má `_ensure_state_schema()` (pro `lead_state` v `sent.db`). Vzorec `PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS ...` je identický. Pokud refaktoruješ, sjednoť do `db.py` se společným `init_all_schemas()`.
- **`RESERVATIONS_DB` cesta** — pokud projekt už definuje `SENT_DB = BASE_DIR / "data" / "sent.db"` se stejným podmíněným Railway přepínačem (`Path("/data/...")` vs `BASE_DIR / "data" / "..."`), použij stejný vzorec, ať se cesty drží na jednom místě (`config.py`).
- **`slug` parametry v endpointech** — pokud projekt už má slug funkce (`_row_slug`, `slug_from_preview_url`, `_web_slug`), nezduplikuj logiku v booking endpointech. Použij existující helper.
- **DB connection pattern** — `with sqlite3.connect(str(RESERVATIONS_DB)) as conn:` se opakuje v každém z 5 booking endpointů. Pokud projekt už má connection helper (context manager), použij ho. Pokud ne, refaktor je dobrá příležitost ho vytvořit.
- **`datetime.now(timezone.utc).isoformat()`** — pokud projekt má helper `_now_utc_iso()` (pravděpodobně v `dashboard.py` nebo `server.py`), použij ho místo opakování inline.
- **Pydantic modely** — pokud projekt už má `LeadData` / podobné modely, drž se stejné konvence pojmenování polí (snake_case, anglické názvy) místo míchání `jmeno` vs `name`.
