# Struktura projektového CLAUDE.md

## Co patří do CLAUDE.md

Pouze instrukce pro chování — co Claude nemůže odvodit z kódu:

- Infrastruktura (Railway IDs, tokeny, endpointy)
- Project Memory — kde hledat dokumentaci
- Task Management — workflow pro daný projekt
- QA — odkazy na větve projektu (viz níže)

## Větve projektu a QA

Projekt může mít více větví (dashboard, Telegram bot, API...). Každá větev má vlastní QA pravidla v `docs/qa/`.

**Vzor v CLAUDE.md:**

```
## QA

Před prací na dashboardu přečti `docs/qa/dashboard.md`.
Před prací na Telegram botu přečti `docs/qa/telegram.md`.
```

**Vzor souboru `docs/qa/dashboard.md`:**

```
# Dashboard — QA
Každá změna musí projít těmito kontrolami...
```

## Co do CLAUDE.md nepatří

- Stack a konvence — Claude vidí z kódu
- Seznam ostatních projektů — irelevantní
- Obecné cíle — patří do globálního CLAUDE.md
- Komunikační styl — patří do globálního CLAUDE.md
- Detailní QA checklisty — patří do `docs/qa/`
- Testovací scénáře — patří do `docs/qa/` nebo `tests/`
