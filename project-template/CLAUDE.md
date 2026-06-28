# [Název projektu]

> [Jedna věta: co projekt dělá a pro koho.]
> Cíl: funkční, nasazená aplikace vhodná do portfolia / pro klienta.

---

## Stack

- **Jazyk:** Python 3.11+
- **Web/API:** [FastAPI + uvicorn / nic, pokud je to skript]
- **DB:** [SQLite / Postgres / žádná]
- **AI:** [OpenAI / Anthropic / žádné]
- **Deploy:** [Railway / jiné] + GitHub
- Závislosti: viz `requirements.txt`

---

## Konvence

- Komentáře a názvy v kódu **anglicky**, komunikace se mnou **česky**
- `.env` pro všechny klíče a tokeny — nikdy necommituj
- Loguj přes `logging`, ne `print()` v produkci
- Preferuj jednoduchost — méně kódu, které funguje, nad složitostí
- Podrobná pravidla: `.claude/rules/` (code-style, testing, api-conventions, security)

### Dočasné a testovací soubory

- Všechny dočasné/ladicí/vizuálně kontrolní soubory dávej výhradně do `tmp/`
- `tmp/` je gitignored — neslouží pro produkční kód ani dokumentaci

---

## Spouštění

- **Lokálně:** [doplň přesný příkaz, např. `.venv/bin/python -m uvicorn server:app --app-dir src`]
- **Produkce:** [Railway spouští `Procfile` / jiné]
- **Testy:** `.venv/bin/pytest` z kořene projektu

> Deploy nikdy sám — až po explicitním pokynu.

---

## Project Memory

Před každou prací zkontroluj:

- `docs/project_notes/key_facts.md` — porty, env proměnné, doména, DB, endpointy
- `docs/project_notes/decisions.md` — ADR: co a proč jsme zvolili
- `docs/project_notes/bugs.md` — problémy, které jsme už řešili
- `tasks/lessons.md` — co se neosvědčilo, co opakovat
- `tasks/todo.md` — aktuální plán a stav

Po každé opravě nebo poučení aktualizuj příslušný soubor.

---

## Task Management

- Netriviální úkol (3+ kroky) → nejdřív plán do `tasks/todo.md`
- Po každé korekci → přidej poučení do `tasks/lessons.md`
- Na začátku session → přečti `tasks/lessons.md`

---

## Komunikace

- Odpovídej **česky**, stručně a k věci
- Jeden správný přístup, ne pět alternativ
- Vysvětluj **proč**, nejen co — cílem je pochopení
- Když něco nevíš nebo si nejsi jistý, řekni to
