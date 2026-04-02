---
name: frontend-live-dashboard
description: >
  HTML/JS dashboard s automatickým refreshem dat bez reloadu stránky.
  Polling přes setInterval + fetch, dark theme tabulka, loading state,
  error handling, dynamický render bez frameworku.

  Použij PROAKTIVNĚ kdykoliv projekt potřebuje:
  - "dashboard", "live data", "real-time zobrazení"
  - "automatický refresh", "data se aktualizují samy"
  - frontend který čte data z FastAPI / REST API
  - tabulka nebo přehled dat bez page reload
  - "chci vidět data na webu", "zobrazit výsledky collectoru"
---

# Frontend Live Dashboard

Jednoduchý, závislostmi nezatížený HTML/JS dashboard. Funguje přímo přes Jinja2 v FastAPI — žádný npm, žádný React.

---

## Základní struktura (`templates/index.html`)

```html
<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard</title>
  <style>
    /* Dark theme základ */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #111;
      color: #e0e0e0;
      font-family: 'Segoe UI', sans-serif;
      font-size: 14px;
      padding: 20px;
    }
    h1 { font-size: 1.4rem; margin-bottom: 20px; }

    /* Tabulka */
    table { width: 100%; border-collapse: collapse; }
    th {
      text-align: left;
      padding: 6px 12px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #666;
      border-bottom: 1px solid #222;
    }
    td {
      padding: 7px 12px;
      border-bottom: 1px solid #1a1a1a;
      color: #0f0;           /* zelená pro hodnoty */
    }
    td.label { color: #e0e0e0; }
    tr:hover td { background: #161616; }

    /* Sekce (skupina symbolů) */
    .section-header td {
      font-size: 10px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #555;
      padding-top: 14px;
      background: transparent;
    }

    /* Status bar */
    #status {
      font-size: 11px;
      color: #555;
      margin-top: 12px;
    }
    #status.error { color: #c00; }
  </style>
</head>
<body>

<h1>Dashboard</h1>
<table id="data-table">
  <thead>
    <tr>
      <th>Symbol</th>
      <th>Průměr</th>
      <th>Min</th>
      <th>Max</th>
      <th>Vzorků</th>
    </tr>
  </thead>
  <tbody id="table-body">
    <tr><td colspan="5" style="color:#555">Načítám...</td></tr>
  </tbody>
</table>
<div id="status"></div>

<script>
const REFRESH_MS = 60_000;  // refresh každých 60 sekund

// Formátování čísla — dynamicky podle velikosti
function fmt(n) {
  if (n === null || n === undefined) return '—';
  if (Math.abs(n) < 0.001) return n.toFixed(6);
  if (Math.abs(n) < 1)     return n.toFixed(4);
  return n.toFixed(2);
}

// Hlavní render funkce
function render(data) {
  const tbody = document.getElementById('table-body');
  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="color:#555">Žádná data</td></tr>';
    return;
  }

  let html = '';
  let lastGroup = null;

  for (const row of data) {
    const group = row.sec_type || 'OTHER';

    // Záhlaví skupiny
    if (group !== lastGroup) {
      html += `<tr class="section-header"><td colspan="5">${group}</td></tr>`;
      lastGroup = group;
    }

    html += `
      <tr>
        <td class="label">${row.label}</td>
        <td>${fmt(row.avg_spread)}</td>
        <td>${fmt(row.min_spread)}</td>
        <td>${fmt(row.max_spread)}</td>
        <td style="color:#555">${row.samples}</td>
      </tr>`;
  }

  tbody.innerHTML = html;
}

// Fetch dat z API
async function refresh() {
  const status = document.getElementById('status');
  try {
    const res = await fetch('/api/averages-all');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    render(data);
    status.className = '';
    status.textContent = `Aktualizováno: ${new Date().toLocaleTimeString('cs-CZ')}`;
  } catch (err) {
    status.className = 'error';
    status.textContent = `Chyba načítání: ${err.message}`;
    // Při chybě nemazat tabulku — zachovej poslední data
  }
}

// Spusť hned a pak každých REFRESH_MS
refresh();
setInterval(refresh, REFRESH_MS);
</script>
</body>
</html>
```

---

## Jak FastAPI servíruje šablonu

```python
from fastapi.responses import HTMLResponse

@app.get("/")
def index():
    return HTMLResponse(content=open("templates/index.html").read())
```

Nebo přes Jinja2 (pro dynamické hodnoty při prvním načtení):

```python
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

---

## Rozšíření: Více sekcí / skupin symbolů

Pokud API vrací `sec_type` nebo jiný grouping klíč:

```javascript
// Příklad dat z API:
// [{ label: "EUR/USD", sec_type: "FOREX", avg_spread: 0.0001, ... },
//  { label: "DAX FUT", sec_type: "FUTURES", avg_spread: 3.0, ... }]

// Seřaď podle sec_type, pak label
data.sort((a, b) => {
  if (a.sec_type !== b.sec_type) return a.sec_type.localeCompare(b.sec_type);
  return a.label.localeCompare(b.label);
});
```

---

## Rozšíření: Graf pro jeden symbol

```javascript
// Přidej tlačítko/select do HTML
// <select id="symbol-select" onchange="loadChart(this.value)"></select>
// <canvas id="chart"></canvas>  → použij Chart.js z CDN

async function loadChart(symbol) {
  const res = await fetch(`/api/history/${symbol}?hours=24`);
  const data = await res.json();
  // data = [{ recorded_at, spread }, ...]
  // napoj na Chart.js nebo vykresli ručně do <canvas>
}
```

---

## Klíčová rozhodnutí — proč takto

| Rozhodnutí | Důvod |
|-----------|-------|
| `setInterval` místo WebSocket | Jednodušší na straně serveru, spolehlivější na Railway, dostačující pro 60s data |
| Žádný React/Vue | Projekt nepotřebuje component tree — přidalo by build krok a složitost |
| Dark theme | Data dashboardy se čtou lépe na tmavém pozadí, menší únava očí |
| `fetch` místo axios | Nativní API, žádná závislost |
| Při chybě zachovej data | UX — lepší vidět stará data než prázdnou tabulku |
| Dynamický formát čísla `fmt()` | Spread může být 0.000001 (forex) nebo 1000 (index) — pevný formát by ztratil přesnost |
