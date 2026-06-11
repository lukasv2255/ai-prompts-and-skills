---
name: responder-llm-judge
description: >
  Postav a ZKALIBRUJ LLM-as-judge pro hodnocení kvality LLM výstupů (tón, sémantika,
  styl) a laď přes něj prompt eval-driven smyčkou. Pokrývá: uzavřený rubric, pass/fail
  osy, deterministické guardy proti halucinaci judge, oddělení advisory vs. gating os,
  triage faillů (vada cíle vs. vada judge), měř → pak laď.

  Použij, když zazní:
  - "LLM judge", "judge na tón", "ohodnoť kvalitu draftů/odpovědí"
  - "regex to nezměří", "jak změřit přirozenost/tón/styl"
  - "laď prompt podle metriky", "eval generátoru/odpovědí"
  - "model halucinuje při hodnocení", "judge dává false-positives"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# LLM judge eval — postav, zkalibruj, laď

Metodika pro měření a ladění kvality LLM výstupů na dimenzích, které **regex/pravidla neumí**
(tón, persona, přirozenost, sémantická věrnost). Klíčová myšlenka: **judge je nástroj, který se
musí zkalibrovat dřív, než mu uvěříš.** Pořadí je vždy `měř → zkalibruj měřidlo → teprve pak laď cíl`.

## Kdy NEpoužívat LLM judge

Dřív než sáhneš po LLM, zeptej se: **jde to změřit deterministicky?** Co umí regex/pravidla
spolehlivě (přítomnost klíčového slova, formát, faktická shoda s ground-truth), tam LLM nedávej —
je dražší, pomalejší a šumí. LLM nech jen na to, co pravidla neumí: „zní to jako člověk?",
konzistence persony, prázdné fráze, sémantická věrnost významu (ne jen slov).

## Postup

### 1. Definuj osy a rubric (uzavřený, ne otevřený)

- Rozlož kvalitu na **2–4 nezávislé osy** (ne jednu vágní „kvalita"). Každá osa = **pass/fail**
  (ne škála 1–5 — pass/fail je stabilnější a líp se kalibruje).
- Pro každou osu napiš **uzavřený seznam** toho, co je FAIL, a explicitně **co NENÍ FAIL**
  (LLM má tendenci over-flagovat — pozitivní výčet „tohle je v pořádku" je stejně důležitý jako
  negativní). Přidej 2–3 konkrétní příklady PASS i FAIL.
- Judge ať vrací **JSON**: per-osa `{pass, reason}` + `flagged_phrases` (doslovné úryvky ze vstupu).
  Použij `temperature=0` a `response_format={"type":"json_object"}`.

### 2. Dej judgi ground-truth kontext, ne jen výstup

- Pokud osa závisí na faktech (věrnost stavu, správnost dat), **předej judgi stejnou ground-truth
  sémantiku, jakou používá generátor** — ne jen holý štítek. Matoucí názvy (např. stav „Přijata
  převodem" = čeká se na platbu) judge jinak čte doslovně a hodnotí špatně.

### 3. ZKALIBRUJ na známých datech (NEpřeskakuj)

- Pusť judge na **existující run** a projdi **každý fail**. Roztřiď:
  - **reálná vada cíle** → patří do ladění generátoru (krok 5),
  - **false-positive judge** → patří do opravy judge (krok 4).
- Agreguj `flagged_phrases` (`sort | uniq -c`) — uvidíš, co judge flaguje nejčastěji a jestli
  to dává smysl.

### 4. Obal LLM deterministickými guardy (proti halucinaci)

LLM judge halucinuje i proti explicitním pokynům. Přidej v kódu **post-processing guardy**:

- **Verbatim ověření:** ponech jen `flagged_phrases`, které jsou **doslovným podřetězcem** vstupu;
  ostatní zahoď (judge si je vymyslel).
- **Exempt seznam:** to, co nikdy není vada (pozdrav, podpis, jádro odpovědi), vyřaď z důkazů.
- **Single-failure-mode guard:** má-li osa jediný reálný failure mode (např. persona = výskyt
  druhého, konfliktního podpisu), **ověř ho stringově** a halucinovaný fail přepiš na PASS.
- Princip: osu smíš nechat FAIL jen na základě textu, který se ve vstupu SKUTEČNĚ vyskytuje.

### 5. Rozhodni gating vs. advisory osy

- **Headline metriku (`all_pass`) počítej JEN z os, kterým judge po kalibraci spolehlivě věří.**
- Osu, která i po zpřísnění promptu dává hodně false-positives **a/nebo dubluje deterministickou
  metriku**, degraduj na **advisory** (mimo `all_pass`) nebo ji zruš. Fakta nech regexu, tón judgi.

### 6. Teprve teď laď cíl a iteruj

- S **důvěryhodným** judgem laď generátor (prompt, few-shot, style guide). Po každé změně, která
  mění výstup, **přegeneruj a přeměř** se stejným seedem.
- U každé iterace se ptej: **„bug judge, nebo bug cíle?"** — nikdy neopravuj generátor kvůli
  šumu judge.
- Pozor: **few-shot příklady přebijí instrukce** — když měníš chování, uprav instrukci I příklady.

## Výstup

- Judge modul s `judge(input, output, ground_truth) -> {osy: {pass, reason}, flagged_phrases, all_pass}`,
  deterministickými guardy a `all_pass` jen z gating os.
- Eval skript s `--judge` flagem, který ukládá verdikt per-záznam + souhrn (per-osa pass-rate,
  advisory osy zvlášť označené).
- Krátký report: per-osa pass-rate, kolik faillů je reálných vs. zbylých, a co je další worklist.

## Anti-patterny

- ❌ Věřit judgi bez kalibrace → ladíš proti šumu.
- ❌ Jedna vágní osa „kvalita 1–10" → nekalibrovatelné, neopakovatelné.
- ❌ LLM osa, co dubluje regex metriku → dvojitá práce, horší výsledek.
- ❌ Žádné guardy → systematické halucinace zkreslí metriku.
- ❌ Ladit generátor a judge ve stejném kroku → nepoznáš, co zabralo.
