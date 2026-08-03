---
name: x-check
description: >
  Prohledá česky psaný AI Twitter (X) a vrátí čerstvé posty vhodné ke komentáři
  pro zvýšení dosahu. Používá Chrome MCP pro přístup k přihlášenému účtu uživatele.

  Použij kdykoliv uživatel říká:
  - "/x check"
  - "zkontroluj twitter"
  - "najdi posty ke komentáři"
  - "co se děje na CZ AI twitteru"
  - "najdi příležitosti ke komentování"
  - "/x replies" / "kdo mi reagoval" / "zkontroluj reakce na moje posty"

---

# x-check — monitoring CZ AI Twitteru

Dva módy:
- **`/x check`** — prohledá profily CZ AI/tech účtů a vrátí čerstvé posty s návrhy komentářů (sekce níže).
- **`/x replies`** — sleduje reakce velkých účtů na moje vlastní posty/replies, zaznamenává, jaké téma je zaujalo, a plní mapu účtů (sekce „Reply tracking mód").

Projektové soubory (v repu AI-brand, `writing/twitter/`):
- `big-accounts-map.md` — mapa velkých účtů, jejich oblíbené teze a reply hooky
- `reply-tracking.md` — log reakcí velkých účtů na můj obsah

---

## Postup

### 1. Získej tab ID (Chrome MCP)
```
tabs_context_mcp (createIfEmpty: true)
```
Zapamatuj si tabId. Pokud tab neexistuje, vytvoří se nový.

### 2. Postupně projdi tyto URL

Vždy: `navigate` → počkej → `javascript_tool` extrakce.

**Profily:**
- `https://x.com/marekl` — Marek Lutonský, tech novinář
- `https://x.com/DavidGrudl` — PHP/tech developer, velká CZ komunita
- `https://x.com/filippodstavec` — Filip Podstavec, AI/tech
- `https://x.com/machal` — Martin Michálek, Vzhůru dolů, frontend/AI
- `https://x.com/lukasersil` — Lukáš Eršil, AI/tech/video, hodně vlastního CZ obsahu
- `https://x.com/tangero` — Patrick Zandl, vibecoding.cz, AI/vývoj, 27k followers
- `https://x.com/JiriCoufal77` — spíš finance, AI občas

**Live search (záloha pokud profily nepřinesou dost):**
- `https://x.com/search?q=%22um%C4%9Bl%C3%A1+inteligence%22+OR+%22AI%22+lang%3Acs+min_faves%3A20&f=live`

### 3. Extrakce tweetů (spusť na každé stránce)

```javascript
const tweets = [];
document.querySelectorAll('article[data-testid="tweet"]').forEach((el) => {
  const text = el.querySelector('[data-testid="tweetText"]')?.innerText || '';
  const userEl = el.querySelector('[data-testid="User-Name"]');
  const nameParts = userEl?.innerText?.split('\n') || [];
  const time = el.querySelector('time')?.getAttribute('datetime') || '';
  const stats = el.querySelector('[role="group"]')?.innerText || '';
  const link = el.querySelector('a[href*="/status/"]')?.href || '';
  if (text.length > 20) tweets.push({
    name: nameParts[0],
    handle: nameParts[1],
    text: text.slice(0, 350),
    time,
    stats,
    link
  });
});
JSON.stringify(tweets.slice(0, 8));
```

### 4. Filtrování

Vyber posty kde:
- Stáří: max 72 hodin od aktuálního data
- Téma: AI, nástroje, automatizace, LLM, workflow — ne čistá politika/zprávy
- Likes/engagement: aspoň nějaký (ne 0)

### 5. Výstup

Vrať 3–5 postů v tomto formátu:

---
**[Jméno] ([handle]) — [datum]**
> "[citace, max 2 věty]"
[link]
Likes: X | Proč komentovat: [1 věta]
> **Návrh komentáře:** *"..."*

---

## Pravidla pro návrh komentáře

- Česky, max 2 věty
- Přidej konkrétní zkušenost nebo poznatek — ne souhlas ("přesně tak")
- Nepůsobit jako AI: žádné "Skvělý postřeh!", žádné em-dash
- Ideální úhel: "u mě to fungovalo takhle..." nebo "viděl jsem opak..."

---

## Technické poznámky

- **Chrome MCP** = ovládá uživatelův přihlášený Chrome → funguje
- **Playwright MCP** = vlastní headless browser bez session → nefunguje pro Twitter
- `lang:cs` search filter nefunguje spolehlivě kombinovaný s anglickými termíny
- Přímé profily CZ účtů jsou spolehlivější než search

---

# Reply tracking mód (`/x replies`)

Cíl: zjistit, **kdo z velkých sledovaných účtů reagoval na moje posty/replies a jaké téma je zaujalo**.
Reakce od velkého účtu = signál, že tenhle úhel u něj funguje → zapiš do mapy a příště na něm stav.

## Postup

### 1. Načti kontext
- Přečti `writing/twitter/big-accounts-map.md` → seznam sledovaných handlů + jejich teze.
- Přečti `writing/twitter/reply-tracking.md` → co už je zaznamenané (ať neduplikuješ).

### 2. Získej tab ID (Chrome MCP)
```
tabs_context_mcp (createIfEmpty: true)
```
Chrome MCP jede přes přihlášený účet → handle uživatele není potřeba.

### 3. Projdi notifikace
`navigate` na `https://x.com/notifications/mentions` → počkej → JS extrakce.
Mentions filtruje jen reakce na můj obsah (ne obecné notifikace).

### 4. Extrakce reakcí
```javascript
const items = [];
document.querySelectorAll('article[data-testid="tweet"]').forEach((el) => {
  const text = el.querySelector('[data-testid="tweetText"]')?.innerText || '';
  const userEl = el.querySelector('[data-testid="User-Name"]');
  const nameParts = userEl?.innerText?.split('\n') || [];
  const time = el.querySelector('time')?.getAttribute('datetime') || '';
  const link = el.querySelector('a[href*="/status/"]')?.href || '';
  const handle = (nameParts.find(p => p.startsWith('@')) || '');
  if (text.length > 5) items.push({ name: nameParts[0], handle, text: text.slice(0, 300), time, link });
});
JSON.stringify(items.slice(0, 25));
```
Tip: pro follow eventy projdi i `https://x.com/notifications`.

### 5. Cross-reference proti mapě
- Nech jen reakce, jejichž `handle` je v `big-accounts-map.md` (velké účty). Ostatní ignoruj.
- U každé zjisti kontext: na který **můj** post/reply reagoval a **jaké bylo téma** mého obsahu
  (pokud není z notifikace jasné, otevři `link` a zjisti vlákno).

### 6. Zápis
Pro každou novou reakci od velkého účtu:
- **`reply-tracking.md`** → nový řádek do tabulky: `datum | @účet | téma mého obsahu | na co reagoval | typ reakce (reply/like/QT/follow) | poznatek`.
- **`big-accounts-map.md`** → do sekce daného účtu, „Doložené reakce", přidej řádek s datem a tématem.
- Když se stejné téma reakce u účtu objeví 2×+, povyš ho na „Oblíbená teze" a uprav „Reply hook".

### 7. Výstup uživateli
Krátký souhrn:
```
Nové reakce od velkých účtů:
- @tangero (dd-mm-yyyy): reply na tvůj post o [téma] → potvrdilo hook „potvrzení jejich teze"
Aktualizoval jsem: reply-tracking.md, big-accounts-map.md (@tangero)
```
Pokud žádná nová reakce od velkých účtů: řekni to a nic nezapisuj.

---

# Reply Router — jak stavět reply, aby reagovali zpět

Router = rozhodovací vrstva mezi „chci reagovat na tenhle post" a „napiš reply".
Cíl: reply vždy zapadne do specializace cílového účtu, takže má důvod odpovědět nebo follownout.

## Vstup
Cílový účet (na jehož post chci reagovat) **nebo** účet, který reagoval mně.

## Logika

1. **Lookup účtu v `big-accounts-map.md`.**
   - Nalezen → načti jeho „Oblíbená teze" + „Reply hook".
   - Nenalezen → fallback na obecná pravidla komentáře (sekce výše) a přidej ho do mapy.

2. **Vyber úhel podle vztahu mého obsahu k jeho tezi** (od nejsilnějšího):
   1. Moje zkušenost **potvrzuje** jeho dlouhodobou tezi → nejsilnější (Zandl case).
   2. Přináším **konkrétní datový bod** k jeho tématu (číslo, benchmark, screenshot).
   3. **Jemný protiklad s důkazem** — „u mě naopak, tady je proč" (víc diskuze, víc rizika).
   4. **Doplňující nuance**, která v postu chybí.

3. **Napiš reply v jeho jazyce:**
   - Použij slovník jeho oboru (dev / SEO / frontend / video…).
   - Konkrétní historka nebo číslo, ne obecné nadšení.
   - Česky, max 2 věty, žádný em-dash, žádné „skvělý postřeh".

4. **Po odeslání** zapiš reply do `myposts.md`/kontextu a čekej na `/x replies`, který zaznamená, jestli reagoval zpět → tím se mapa učí.

## Výběr cíle (kam vůbec investovat reply)
Prioritizuj účty, kde už mám doloženou reakci (mapa) > velký dosah + jasná teze > okrajové AI účty (nízká priorita, např. @JiriCoufal77).

## Zpětná vazba (proč to celé funguje)
`/x replies` → doloží reakci → povýší téma na tezi → router příště sáhne po ověřeném hooku.
Bez logu bys stavěl reply od nuly pokaždé; s logem se strategie u každého účtu zpřesňuje.
