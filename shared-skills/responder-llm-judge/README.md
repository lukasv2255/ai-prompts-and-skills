# llm-judge-eval

Skill pro stavbu a kalibraci **LLM-as-judge** — hodnocení kvality LLM výstupů na dimenzích,
které regex/pravidla neumí (tón, persona, přirozenost, sémantická věrnost), a ladění promptu
eval-driven smyčkou.

Hlavní princip: **judge je měřidlo, které se musí zkalibrovat dřív, než mu uvěříš.** Pořadí
práce je vždy `měř → zkalibruj měřidlo → teprve pak laď cíl`. Bez kalibrace ladíš generátor
proti halucinacím judge.

## Co skill řeší

- Návrh os a uzavřeného pass/fail rubricu (ne vágní škála).
- Kalibrace na známých datech + triage faillů (vada cíle vs. false-positive judge).
- Deterministické guardy kolem LLM výstupu proti systematickým halucinacím.
- Rozhodnutí gating vs. advisory osy — co měřit LLM a co nechat regexu.

## Kdy ho použít

Když potřebuješ změřit „zní to jako člověk?", konzistenci tónu/persony, prázdné fráze nebo
sémantickou věrnost — a regex na to nestačí. NEpoužívej ho na to, co jde změřit deterministicky.

## Původ

Vydestilováno z práce na `mail-agent` (responder): LLM judge na tón draftů + ladění generátoru.
Detailní projektové lekce viz `tasks/lessons.md` v daném projektu.
