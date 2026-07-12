---
name: precision-mode
description: Pouzij pro tezke, rizikove nebo vicekrokove ukoly, kde je potreba zamknout scope pred implementaci. Hodi se na bugfixy, klientsky feedback, debug, zmeny zasahujici vice souboru, produkcni opravy, nebo kdyz uzivatel potrebuje rozhodnout minimalni fix vs. dalsi scope.
---

# Precision Mode

Tohle je operacni disciplina pro ukoly, kde nestaci jit rovnou do kodu. Cilem je zamknout nejkratsi spolehlivou cestu a snizit scope creep.

## Postup

### 1. Target lock

Nejdric stanov:

- co ma byt presne vysledek
- co je minimalni bezpecny fix nebo vystup
- co uz patri do dalsi davky
- podle ceho pozname, ze je hotovo

### 2. Ground truth

Pracuj z dukazu:

- konkretni soubory
- logy
- testy
- data
- screenshoty
- chovani aplikace

Zmineny soubor nebo domnenka nejsou dukaz.

### 3. Pressure test

Pred implementaci zkontroluj:

- kde hrozi scope creep
- jaka zavislost nebo vedlejsi efekt to muze rozbit
- jestli neni oprava zbytecne siroka
- co je nejpravdepodobnejsi chyba v uvaze

### 4. Proof

Nevrcej "hotovo" bez overeni. Uved:

- co jsi overil
- jak jsi to overil
- co zustava neoverene

## Kdy pouzit

- bugfix s vice navaznymi symptomy
- klientsky feedback, ktery muze rozsirit scope
- produkcni oprava
- zmena zasahujici vice souboru
- rozhodovani mezi rychlym fixem a plnou opravou

## Vystupni format

### Precision plan

- **Cil:**
- **Minimalni fix ted:**
- **Mimo aktualni scope:**
- **Prvni soubory / mista ke kontrole:**
- **Acceptance criteria:**
- **Rizika:**
- **Nejkratsi spolehliva cesta:**
- **Overeni po zmene:**
