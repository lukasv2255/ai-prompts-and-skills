---
name: new-agent-project
description: Scaffold nového Python AI agenta. Použij když uživatel říká "nový projekt", "chci postavit agenta", nebo "začni nový bot/agent".
allowed-tools: Read, Write, Edit, Glob, Bash
---

# New Agent Project Scaffold

Vytvoř kompletní strukturu nového Python AI projektu a projdi všechny fáze plánování.

---

## Fáze 1 — Průzkum (vždy specifický pro projekt)

Zeptej se (nebo zjisti z kontextu):

- Jaký problém firma/uživatel řeší a co teď dělá ručně?
- Nakresli pipeline: `[Vstup] → [Zpracování] → [Výstup]`
- Jaké typy vstupů systém dostává? (e-maily, formuláře, zprávy...)
- Jaké externí systémy jsou zapojeny? (API, DB, CRM, inbox...)
- Kdo bude systém provozovat — vývojář nebo klient sám?

---

## Fáze 2 — Zmapuj přístupy k externím službám

Sestav tabulku:

| Služba | Přístup (✅/❌/❓) | Jak obejít bez přístupu |
| ------ | ------------------ | ----------------------- |
| ...    | ...                | ...                     |

Přístup určuje pořadí kroků a co lze testovat bez závislostí.

---

## Fáze 3 — Architektura

- Identifikuj **pevné části** (sdílené mezi projekty) vs. **variabilní** (mění se per klient)
- Rozhraní vstupního systému = jediný soubor který se mění mezi projekty
- DB schema vždy první, deployment vždy poslední

---

## Fáze 4 — Knowledge Base / data

- Nejdřív KB, pak kód — agent je tak dobrý jako data která má
- Malá KB → textové soubory v `prompts/`
- Velká KB → vektorová databáze (RAG/ChromaDB)
- `prompts/` = produkční data, `tests/` = simulovaná testovací data (fixtures)

---

## Fáze 5 — Schvalovací kanál

- Vývojář/test → Telegram
- Klient bez IT → Web dashboard
- Firma se Slackem → Slack s tlačítky
- Ověřená produkce → auto-send pro low-risk, schválení jen pro citlivé typy

---

## Fáze 6 — Chybějící informace

- Systém neeskaluje rovnou — navrhne výstup nebo se zeptá na doplnění
- Člověk doplní → systém vygeneruje nový výstup ke schválení
- Timeout bez reakce → zalogovat jako `needs_human`

---

## Fáze 7 — Testování bez reálného prostředí

Fixtures = vymyšlená data simulující reálný systém (`tests/`).

| Závislost            | Jak testovat                    |
| -------------------- | ------------------------------- |
| DB                   | SQLite lokálně                  |
| Externí feed/API     | statický soubor `fixtures/`     |
| Scraping             | HTML snapshot v `fixtures/`     |
| Placené API          | mock server (FastAPI localhost) |
| Produkční systém     | DRY_RUN mode                    |
| Produkční API (test) | jeden testovací záznam          |

### Živé demo pro klienta (bez přístupu k jeho inboxu)

Klient nechce dát přístup k inboxu ani datům, ale chce vidět reálný průběh.

Použij vlastní testovací inbox (např. `newagent7878@gmail.com`) a KB s vymyšlenými daty klienta:

```
Klient pošle e-mail na testovací adresu
  → agent přečte přes Gmail API
  → Telegram: návrh odpovědi ke schválení
  → /yes → agent odešle odpověď zpět klientovi
```

Klienta lze přidat do Telegram skupiny — vidí návrhy a schvalování živě.

---

## Fáze 8 — Nasazení postupně (shadow mode)

- `DRY_RUN=true` → jen logy, žádné notifikace
- Shadow mode → systém generuje výstupy, člověk pracuje paralelně, porovnání
- Produkce → nejdřív low-risk typy, pak rozšiřovat

---

## Fáze 9 — Pricing

- Jednoduchá integrace → nižší setup fee
- Složitá integrace (OAuth, třetí systémy, routing) → vyšší setup fee
- Měsíční provoz = infrastruktura + monitoring + drobné úpravy

---

## Fáze 10 — Správa po nasazení

- KB aktualizuje klient nebo vývojář na vyžádání
- Credentials a tokeny mají expiraci → nastavit připomenutí
- Logy monitoruje vývojář, klient hlásí problémy

---

## Scaffold — Vytvoř strukturu projektu

**Pravidlo:** Projekt musí fungovat lokálně před tím než řešíš Railway nebo jiný cloud.

### Cesta projektu (cross-platform)

```python
import os, platform
base = os.path.expanduser("~")
# Mac:     ~/claude-code/<nazev>/
# Windows: C:\Users\<username>\claude-code\<nazev>\
project_path = os.path.join(base, "claude-code", "<nazev-projektu>")
```

### Adresářová struktura

```
<projekt>/
  src/
    __init__.py
    classifier.py       ← klasifikace vstupů
    responder.py        ← generování odpovědí
    notifier.py         ← Telegram / Slack / web
    mail_client.py      ← variabilní: Gmail / IMAP / Graph / Helpdesk
    kb_loader.py        ← variabilní: soubory (demo) nebo DB klienta (produkce)
  prompts/              ← produkční KB (systémové prompty, ceník, FAQ...)
  tests/
    fixtures/           ← vymyšlená data pro testování bez reálného inboxu
    projekt_XX/         ← per-projekt testovací emaily a KB
  docs/
    key_facts.md        ← API klíče, porty, Railway IDs
    decisions.md        ← co a proč jsme zvolili
    bugs.md             ← problémy které jsme řešili
    issues.md           ← otevřené otázky
  tasks/
    todo.md
    lessons.md
  logs/
    .gitkeep
  main.py
  requirements.txt
  .env.example
  .gitignore
  Procfile
  README.md
```

### requirements.txt (základ)

```
python-telegram-bot==20.7
openai==1.12.0
python-dotenv==1.0.0
```

### .env.example

```
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DRY_RUN=true
KB_SOURCE=file        # "file" pro demo/dev, "db" pro produkci s DB klienta
```

### .gitignore

```
.env
token.json
credentials.json
logs/*.log
__pycache__/
*.pyc
.DS_Store
```

### Procfile

```
worker: python main.py
```

### main.py skeleton

```python
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/agent.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Agent spuštěn.")


if __name__ == "__main__":
    asyncio.run(main())
```

### key_facts.md

```markdown
# Key Facts — <Název projektu>

## Stack

- Jazyk: Python 3.11+
- AI: OpenAI GPT-4o-mini
- Deployment: Railway + GitHub

## Infrastructure

- Railway token: [doplnit]
- Railway Project ID: [doplnit po vytvoření]
- Railway Service ID: [doplnit po vytvoření]
- GitHub repo: [doplnit]
```

---

## Po scaffoldu

1. Inicializuj git: `git init && git add . && git commit -m "init"`
2. Vytvoř GitHub repo a pushni
3. Připomeň uživateli: `npm install -g @railway/cli`
4. Vrať se k Fázi 1 a projdi plánování pokud ještě neproběhlo
