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

---

# x-check — monitoring CZ AI Twitteru

Prohledá profily českých AI/tech účtů a vrátí 3–5 čerstvých postů s návrhy komentářů.

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
- `https://x.com/marekl`
- `https://x.com/DavidGrudl`
- `https://x.com/JiriCoufal77`

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
