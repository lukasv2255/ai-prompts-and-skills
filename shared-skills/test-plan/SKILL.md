---
name: test-plan
description: Rozhodni, CO a JAK testovat, jeste pred psanim testu. Pouzij kdyz uzivatel rika "jak to otestovat", "priprav testy", "napln testy na tuhle featuru", "test coverage", "jak overit tuhle implementaci", nebo pred testovanim slozitejsi zmeny, ktera saha na vic vrstev (LLM vystup, side-efekty, DB, integrace). Nepsat testy naslepo — nejdriv testovaci matice.
---

# Test Plan

Nejvic promarnene prace u testu vznika tim, ze se **spatna vrstva testuje spatnym nastrojem**:
`assert` na LLM vystup (flakuje), LLM judge na to, co umi regex (drahe a sumi), unit test na
invariant, ktery zije az v callerovi. Tenhle skill je rozhodovaci krok PRED psanim testu:
rozlozi implementaci na vrstvy podle testovatelnosti a kazde priradi spravny nastroj.

Nepiseš zde testy. Vracis **testovaci matici + poradi + pasti**. Domenove agnosticke.

## Postup

### 1. Rozloz zmenu na vrstvy podle testovatelnosti

Projdi kod a zaraď kazdy povrch do jedne ze ctyr vrstev — vrstva urcuje nastroj:

| Vrstva | Poznávací znak | Nastroj |
|---|---|---|
| **Deterministicka** | stejny vstup → stejny vystup (formatovani, vypocet, pravidlo, parsing) | **unit test / assert** |
| **Nedeterministicka (LLM)** | vystup generuje model (ton, text, klasifikace) | **LLM-as-judge** (viz `responder-llm-judge`) |
| **Side-effect** | zapis do DB, sit, fronta, soubor, notifikace | **spy + mock** (over ze/co se stalo) |
| **Integrace / invariant** | pravidlo napric moduly ("posila se jen odsud", "jen kdyz X") | **invariant test** nad realnym call-site |

Pravidlo cislo jedna: **co umi regex spolehlivě (pritomnost, format, fakticka shoda), tam LLM nedavej.**
LLM judge nech jen na to, co regex neumi (prirozenost, ton, semantika).

### 2. Kazde vrstve priraď nastroj a rozhodni gating vs advisory

- Deterministicke osy → tvrde gating (headline pass/fail).
- LLM judge osy → **advisory, dokud neni judge zkalibrovany** (nevaz do headline metriky).
- U side-efektu: nahraď realny efekt spionem, ktery zaznamena volani (jestli a s cim), a
  mockuj drahe/externi zavislosti (OpenAI, HTTP, background thread).

### 3. Vypis guardy a pasti (tady se to typicky rozbije)

Projdi implementaci a explicitne oznac:

- **Fallback vetve** — kazde `try/except` / `or default` je vlastni testovatelny scenar.
- **Opt-out / feature flag vetve** — zapnuto i vypnuto.
- **Idempotence** — spusti se to dvakrat / na duplicitu → nesmi zdvojit efekt. Najdi, kde ten
  guard fyzicky zije (casto v callerovi `if created:`, ne ve funkci samotne) a testuj tam.
- **Cache** — pri ladeni vstupu invaliduj cache klic, jinak testujes stary vystup.
- **Izolace testu** — globalni stav (env, module-level konstanty, sdilena DB) → over, ze se
  soubory netlucou pri behu naraz, ne jen jednotlive.

### 4. Vrať matici + poradi

Vystup je tabulka `povrch → vrstva → nastroj → gating/advisory` plus poradi:
levne a deterministicke driv, drahe/LLM/integracni pozdeji. A jednu vetu "co udelat hned".

## Kdy pouzit

- Featura saha na vic vrstev (typicky: LLM vystup + DB zapis + nejaky invariant).
- Pred testovanim rizikove nebo produkcni zmeny.
- Kdyz nevis, jestli neco patri do unit testu, judge, nebo integracniho testu.

## Kdy nepouzit

- Trivialni cista funkce s jednim vstupem/vystupem — napiš rovnou unit test, matice je overkill.
- Kdyz uz test plan existuje a jen se dopisuje jeden pripad.

## Failure modes

- ❌ `assert` na LLM vystup → flaky. Patri do LLM-judge (advisory).
- ❌ LLM judge na format/cislo/emoji → drahe a sumi. Patri do regexu (gating).
- ❌ Idempotence testovana ve funkci, kdyz guard zije v callerovi → invariant neni pokryty.
- ❌ Testy zelene jednotlive, cervene naraz → nepokryta izolace (globalni stav).
- ❌ Ladeni cile i mena zaroven → nepoznas, co zabralo. Nejdriv zmer, pak laď.

## Quality gate

Plan je pouzitelny, kdyz:

- kazdy povrch zmeny ma prirazenou vrstvu i nastroj (zadny "nejak to otestujeme"),
- kazda fallback / opt-out / idempotence vetev ma radek v matici,
- je jasne, ktere osy jsou gating (verime) a ktere advisory (zatim ne),
- poradi jde od nejlevnejsich a nejdeterministictejsich testu k drahym.

## Zarazeni ve workflow-routeru

Skupina 1 (Zadani a rozhodovani), vedle `precision-mode` a `completion-audit`. Logicka trojice:
**precision-mode** zamkne scope → **test-plan** zamkne jak to overit → **completion-audit** potvrdi
ze hotovo.
