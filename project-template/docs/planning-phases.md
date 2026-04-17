# Plánování nového projektu — Fáze

> Přečti před zahájením implementace nového projektu.

**Fáze 1 — Průzkum** _(vždy specifický pro projekt)_

- Jaký problém firma/uživatel řeší a co teď dělá ručně?
- Nakresli pipeline: `[Vstup] → [Zpracování] → [Výstup]`
- Jaké typy vstupů systém dostává?
- Jaké externí systémy jsou zapojeny? (API, DB, CRM...)
- Kdo bude systém provozovat — vývojář nebo klient sám?

**Fáze 2 — Zmapuj přístupy k externím službám**

- Tabulka: Služba | Přístup (✅/❌/❓) | Jak obejít bez přístupu
- Přístup určuje pořadí kroků a co lze testovat bez závislostí

**Fáze 3 — Architektura** _(kostra stejná, části se mění)_

- Identifikuj pevné části (sdílené mezi projekty) vs. variabilní (mění se per klient)
- Rozhraní vstupního systému = jediný soubor který se mění mezi projekty
- DB schema vždy první, deployment vždy poslední

**Fáze 4 — Knowledge Base / data** _(pokud projekt pracuje s daty klienta)_

- Nejdřív KB, pak kód — agent je tak dobrý jako data která má
- Malá KB → textové soubory v `prompts/`
- Velká KB → vektorová databáze (RAG/ChromaDB)
- `prompts/` = produkční data pro konkrétní nasazení (prázdné dokud není reálný klient)
- `tests/` = vše testovací — KB, testovací emaily, prompty, fixtures — i pro budoucí projekty
- Zdroj dat abstrahuj přes `kb_loader.py` — demo čte ze souborů (`KB_SOURCE=file`), produkce z DB klienta (`KB_SOURCE=db`). Agent (classifier, responder) se nemění.

**Fáze 5 — Schvalovací kanál** _(pokud člověk schvaluje výstupy)_

- Vývojář/test → Telegram
- Klient bez IT → Web dashboard
- Firma se Slackem → Slack s tlačítky
- Ověřená produkce → auto-send pro low-risk, schválení jen pro citlivé typy

**Fáze 6 — Chybějící informace**

- Systém neeskaluje rovnou — navrhne výstup nebo se zeptá na doplnění
- Člověk doplní → systém vygeneruje nový výstup ke schválení
- Timeout bez reakce → zalogovat jako `needs_human`

**Fáze 7 — Testování bez reálného prostředí**

- Fixtures = vymyšlená data simulující reálný systém (`tests/`)
- Testovací vstupy = konkrétní případy s očekávaným výsledkem
- Výsledková tabulka: klasifikace správná? Výstup správný? Eskalace správná?

| Závislost            | Jak testovat                    |
| -------------------- | ------------------------------- |
| DB                   | SQLite lokálně                  |
| Externí feed/API     | statický soubor `fixtures/`     |
| Scraping             | HTML snapshot v `fixtures/`     |
| Placené API          | mock server (FastAPI localhost) |
| Produkční systém     | DRY_RUN mode                    |
| Produkční API (test) | jeden testovací záznam          |

**Fáze 8 — Nasazení postupně (shadow mode)**

- `DRY_RUN=true` → jen logy, žádné notifikace
- Shadow mode → systém generuje výstupy, člověk pracuje paralelně, porovnání
- Produkce → nejdřív low-risk typy, pak rozšiřovat

**Fáze 9 — Pricing** _(škáluje podle složitosti integrace)_

- Jednoduchá integrace → nižší setup fee
- Složitá integrace (OAuth, třetí systémy, routing) → vyšší setup fee
- Měsíční provoz = infrastruktura + monitoring + drobné úpravy

**Fáze 10 — Správa po nasazení**

- KB aktualizuje klient nebo vývojář na vyžádání
- Credentials a tokeny mají expiraci → nastavit připomenutí
- Logy monitoruje vývojář, klient hlásí problémy

**Pravidlo deploymentu:** Projekt musí fungovat lokálně před tím než řešíš Railway nebo jiný cloud.
