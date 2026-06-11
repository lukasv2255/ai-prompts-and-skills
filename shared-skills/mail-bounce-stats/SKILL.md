---
name: mail-bounce-stats
description: >
  Přidá do mail-agent instance bounce/reject statistiku do CRM/Stats dashboardu.
  Skenuje IMAP schránku, najde bounce maily od MAILER-DAEMON/postmaster,
  parsuje DSN Status (RFC 3464) a rozlišuje:
   - hard reject (5.1.x bad address, 5.7.x policy, generický 5.x.x) → mrtvý lead
   - soft bounce (5.2.2 mailbox full, 4.x.x temp, full/quota v textu) → lead žije
   - none (bez DSN — DMARC reporty apod.) → ignorováno

  Použij kdykoliv uživatel říká: "kolik mi přišlo rejected", "bounce stats",
  "deliverability", "kolik leadů je mrtvých", "kolik mi to vrátilo",
  "rejected mail", "undelivered". Funguje nad libovolnou IMAP schránkou.
---

# Mail Bounce Stats

Bounce klasifikace nad celou IMAP schránkou. Cílem je v CRM/Stats panelu
vidět **kolik leadů je opravdu mrtvých** (hard reject) vs **kolik dočasně
nelze doručit** (soft bounce). Funguje napříč všemi sdílenými instancemi
mail-agenta na stejné schránce.

---

## Co skill přidá

1. **`src/modules/inbox_stats.py`** — Python modul s funkcí `count_bounce_stats()`,
   vrací dict:

   ```json
   {
     "rejected": 3, // hard rejects
     "soft_bounces": 5, // mailbox full, temp...
     "bounces_total": 8, // hard + soft
     "sent_total": 441, // počet mailů v \Sent složce
     "folders": ["INBOX", "reports"],
     "per_folder": { "INBOX": 3, "reports": 0 },
     "sent_folders": ["Sent"],
     "error": null
   }
   ```

2. **Dashboard endpoint** (`src/dashboard.py`):

   ```python
   @app.get("/api/inbox/bounce-stats")
   def api_inbox_bounce_stats(request: Request):
       _check_token(request)
       from src.modules.inbox_stats import count_bounce_stats
       return count_bounce_stats()
   ```

3. **CRM/Stats dlaždice** (`templates/dashboard.html`) — 6 stat-cardů:
   Hard rejected | Soft bounces | Bounces celkem | Odesláno (schránka) |
   Hard reject ratio | Bounce ratio

---

## Pipeline (jak klasifikace funguje)

1. **IMAP LIST** → vybere všechny složky **kromě** těch s atributem
   `\Sent`, `\Drafts`, `\Trash`, `\Junk`, `\All`, `\Noselect`. Outgoing
   složky se přeskočí, aby se nepočítaly vlastní odeslané maily.

2. **IMAP SEARCH FROM** "MAILER-DAEMON" + "postmaster" v každé složce →
   bounce kandidáti. Per složka dedup podle UID.

3. **IMAP FETCH BODY.PEEK[]** každého kandidáta (PEEK nezmění `\Seen`
   flag). V těle hledá DSN `Status: X.Y.Z` (RFC 3464).

4. **Klasifikace** podle Status + textu:

   | Status          | Text v těle                             | Klasifikace                            |
   | --------------- | --------------------------------------- | -------------------------------------- |
   | `5.1.x`         | —                                       | **hard** (bad address)                 |
   | `5.7.x`         | —                                       | **hard** (policy / blocked / spam)     |
   | `5.2.2`         | —                                       | **soft** (mailbox full)                |
   | `5.x.x`         | obsahuje "full"/"quota"/"plná schránka" | **soft**                               |
   | `5.x.x`         | neobsahuje                              | **hard** (generický permanent failure) |
   | `4.x.x`         | —                                       | **soft** (temporary)                   |
   | žádný `Status:` | —                                       | **none** (DMARC report, auto-mail)     |

5. **`\Sent` složka(y)** se počítá zvlášť přes IMAP SEARCH ALL — to je
   denominator pro reject/bounce ratio.

---

## Instalace do instance

### Závislosti

- Mail-agent template repo (musí mít `src/imap_credentials_store.py` s funkcí
  `load_credentials_or_env()` vracející `imap_host/port/user/password`)
- Python 3.10+ (kvůli `tuple[set[str], str] | None` syntaxi)
- IMAP přístup ke schránce (lokálně přes `.env`, na Railway přes vault)

### Kroky

**1. Zkopíruj modul:**

```bash
cp ~/ai-prompts-and-skills/shared-skills/mail-bounce-stats/inbox_stats.py \
   src/modules/inbox_stats.py
```

**2. Přidej endpoint do `src/dashboard.py`** (najdi vhodné místo mezi
existujícími `@app.get(...)` endpointy):

```python
@app.get("/api/inbox/bounce-stats")
def api_inbox_bounce_stats(request: Request):
    _check_token(request)
    from src.modules.inbox_stats import count_bounce_stats
    return count_bounce_stats()
```

**3. Přidej UI do `templates/dashboard.html`** v JS sekci CRM/Stats:

```javascript
// State
let _bounceStats = null;
let _bounceError = null;

async function refreshBounceStats() {
  try {
    const res = await apiFetch("/api/inbox/bounce-stats");
    const data = await res.json();
    _bounceStats = data;
    _bounceError = data.error || null;
  } catch (_) {
    _bounceStats = null;
    _bounceError = "fetch failed";
  }
  renderBounceTiles();
}

function renderBounceTiles() {
  const el = document.getElementById("bounce-stats-tiles");
  if (!el) return;
  const s = _bounceStats || {};
  const fmt = (n) => (typeof n === "number" ? n.toLocaleString("cs-CZ") : "…");
  const pct = (num, den) =>
    typeof num === "number" && typeof den === "number" && den > 0
      ? ((num / den) * 100).toFixed(1) + " %"
      : "—";
  const title = _bounceError
    ? `title="${_bounceError}"`
    : 'title="IMAP scan. Hard = adresa mrtvá/blokuje. Soft = lead žije."';

  el.innerHTML = `
    <div class="stat-card" ${title}>
      <div class="stat-label">Hard rejected</div>
      <div class="stat-value" style="color:#e57373">${fmt(s.rejected)}</div>
    </div>
    <div class="stat-card" ${title}>
      <div class="stat-label">Soft bounces</div>
      <div class="stat-value" style="color:#e0a060">${fmt(s.soft_bounces)}</div>
    </div>
    <div class="stat-card" ${title}>
      <div class="stat-label">Bounces celkem</div>
      <div class="stat-value">${fmt(s.bounces_total)}</div>
    </div>
    <div class="stat-card" ${title}>
      <div class="stat-label">Odesláno (schránka)</div>
      <div class="stat-value">${fmt(s.sent_total)}</div>
    </div>
    <div class="stat-card" ${title}>
      <div class="stat-label">Hard reject ratio</div>
      <div class="stat-value">${pct(s.rejected, s.sent_total)}</div>
    </div>
    <div class="stat-card" ${title}>
      <div class="stat-label">Bounce ratio</div>
      <div class="stat-value">${pct(s.bounces_total, s.sent_total)}</div>
    </div>`;
}
```

A do HTML sekce CRM/Stats:

```html
<div id="bounce-stats-tiles" style="display:flex;gap:12px;flex-wrap:wrap"></div>
```

Plus volat `refreshBounceStats()` při loadu CRM/Stats tabu.

**4. Test z příkazové řádky** (bez dashboardu):

```bash
python3 -m src.modules.inbox_stats
```

Vrátí JSON s aktuálním stavem schránky.

---

## Pravidla vlastnictví (mail-agent template)

Per `CLAUDE.md` mail-agent template:

- `src/modules/inbox_stats.py` — **instance-owned** (template do něj nesahá) ✓
- `src/dashboard.py` — **template-owned** — přidání endpointu je porušení;
  v praxi se to už dělá pro jiné instance-specific endpointy (`/api/campaign/*`)
- `templates/dashboard.html` — **template-owned** — stejná situace

Při merge z `template/main` mohou nastat konflikty v dashboardu/HTML.
Řeší se ručně — endpoint a JS jsou samostatné bloky, takže merge je
zvládnutelný.

---

## Pozor / edge cases

- **DMARC reporty** (`MAILER-DAEMON@centrum.cz` posílá denně XML report
  o validaci tvé domény) — match na FROM, ale nemají `Status:` header →
  klasifikované jako `none` → správně se nezapočítají.
- **Generický 5.0.0** — některé MTA (webglobe.com) posílá pro full mailbox
  místo 5.2.2. Pravidlo "5.x.x s full/quota v textu" tohle chytí.
- **Více bounces stejné adresy** — počítají se každý zvlášť (3 maily na
  jednu adresu = 3 bounces). Pokud chceš dedup per recipient address,
  parsuj `Final-Recipient:` header a deduplikuj — neimplementováno.
- **Velké schránky** — pro každý bounce kandidát se dělá FETCH těla.
  Pro 1000+ bounces může scan trvat desítky sekund. Cache výsledku na
  straně dashboardu, nebo persistovat stav per UID.
- **Jiný credentials store** — pokud instance nepoužívá
  `src.imap_credentials_store.load_credentials_or_env`, uprav
  `_connect_imap()` v modulu (3 řádky).

---

## Origin

Vyvinuto pro `mail-agent-webredesign` (ubytovani instance) na sdílené
schránce, kde se navzájem mísí maily z víc instancí. Cílem bylo dostat
"bounce dashboard" jako Postmaster Tools, ale nad vlastní IMAP — nezávisle
na poskytovateli, bez SMTP relay nebo external SaaS.
