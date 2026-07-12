---
name: completion-audit
description: Over, jestli je prace opravdu hotova a pripravena k odevzdani, merge nebo deployi. Pouzij kdyz uzivatel rika "zkontroluj, jestli je to hotove", "muze to do produkce", "je to pripraveny pro klienta", "udelej finalni check", nebo po vetsim zasahu do kodu, dat nebo konfigurace.
---

# Completion Audit

Audituj vysledek skepticky, ale vecne. Neber dokoncenost na slovo. Over, co se opravdu zmenilo a co je skutecne potvrzene.

## Co kontrolovat

### 1. Shoda se zadanim

- je splneno puvodni zadani
- jsou pritomne vsechny pozadovane vystupy
- nebyl potichu rozsiren nebo zmenen scope

### 2. Dukazy

- existuji zmenene soubory
- sedi cesty, nazvy a artefakty
- tvrzeni v odpovedi odpovidaji tomu, co je v souborech nebo vystupech

### 3. Overeni

Pro kod a data kontroluj:

- testy
- build
- lint
- typecheck
- prikazy
- sample input/output
- realne chovani po zmene

Kdyz neco nejde overit, rekni to presne.

### 4. Rizika

Hledej:

- neoverene domnenky
- chybejici krok v deployi nebo migraci
- zmenu popsanych oprav, ktere nejsou opravdu zapsane
- vedlejsi efekty
- bezpecnostni nebo datove riziko

## Vystupni format

### Audit verdict

- **Verdict:** verified / partly verified / not verified
- **Pokryti zadani:**
- **Co bylo overeno:**
- **Co se nepodarilo overit:**
- **Problemy:**
- **Dalsi nutny krok:**

## Pravidla

- Kdyz je to v poradku, rekni to jasne.
- Kdyz neco chybi, rekni presne co.
- Neopravuj siroce. Audit ma primarne hodnotit, ne prepisovat pul projektu.
