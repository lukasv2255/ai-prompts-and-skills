---
name: workflow-router
description: Doporuci workflow, poradi kroku a vhodne skilly podle toho, co se uzivatel prave chysta delat. Pouzij kdyz uzivatel rika veci jako "budu implementovat feedback od klienta", "jdu debugovat", "chci nasadit", "zacinam novy projekt", "potrebuju review", "budu migrovat data", "chci rozjet AI trenera", "resim mail agenta" nebo "stavim trading dashboard".
---

# Workflow Router

Urci nejvhodnejsi pracovni postup pro aktualni ukol. Neodpovidej obecne. Nejdric zarad praci do faze projektu, potom vyber nejvhodnejsi skupinu skillu a nakonec doporuc konkretni poradi kroku.

Vzdy vrat kratky, prakticky navrh:

1. Co je cil teto prace
2. Jaka je faze projektu
3. Jake workflow zvolit
4. Jake skilly pouzit a v jakem poradi
5. Na co si dat pozor

Pokud je zadani nejasne, udelej rozumny pracovni predpoklad a explicitne ho oznac.

## Skupiny skillu

### 1. Zadani a rozhodovani

Pouzij pro nejasne, rizikove nebo vetsi ukoly.

- `brief-builder`: prevod vagnich poznamek na pracovni brief
- `task-router`: volba workflow podle rizika, ceny a slozitosti
- `precision-mode`: target lock, evidence, pressure test, proof
- `agent-chain`: navrh viceagentoveho workflow
- `completion-audit`: overeni, ze je prace opravdu hotova
- `method-capture`: prevod dobreho postupu do reusable skillu

### 2. Implementace a kvalita

Pouzij pri zmenach kodu, review, pred commitem a pred nasazenim.

- `code-review`
- `security-review`

### 3. Start noveho projektu nebo nove vetve produktu

Pouzij na scaffold, architekturu a prvni funkcni kostru.

- `new-agent-project`
- `railway-collector-app`
- `fastapi-ingest-api`

### 4. Data, ingest, dashboard a databaze

Pouzij kdyz system sbira, presouva nebo zobrazuje data.

- `db-migrate`
- `frontend-live-dashboard`
- `railway-db`
- `git-data-sync`

### 5. Deploy, provoz a runtime problemy

Pouzij pri nasazeni, redeployi, runtime chybach a dlouho bezicich procesech.

- `railway-deploy`
- `railway-redeploy`
- `debug-railway-env`
- `launchd-agent`
- `tray-app`
- `tray-start`

### 6. Kanaly, notifikace a komunikace

Pouzij kdyz je soucasti reseni bot, schvalovani nebo notifikace.

- `telegram-bot-setup`

### 7. Knowledge base a obsah

Pouzij pro ingest obsahu, RAG a pripravu AI znalostni vrstvy.

- `yt-transcripts`
- `yt-rag`
- `yt-gpt-builder`

### 8. Git a synchronizace mezi pocitaci

Pouzij kdyz je potreba push, pull nebo synchronizace pracovniho prostredi.

- `git-push`
- `git-push-pull`
- `sync-pull-mac`
- `sync-pull-pc`
- `sync-push-mac`
- `sync-push-pc`

### 9. Marketing a launch

Pouzij jen kdyz jde o launch produktu nebo sluzby, ne o bezny engineering.

- `launch-campaign`

## Faze projektu

Zarad ukol do jedne z techto fazi:

1. Zamer a zpresneni zadani
2. Navrh reseni a architektura
3. Scaffold a prvni implementace
4. Integrace a napojeni na sluzby
5. Debug a stabilizace
6. Review, security a verifikace
7. Deploy a provoz
8. Rust, opakovani a znovupouziti

## Doporucena workflow podle typu ukolu

### Kdyz uzivatel implementuje feedback od klienta

Pouzij:

1. `brief-builder`, pokud feedback neni uplne jasny nebo je rozptyleny v bodech
2. `precision-mode`, pokud zmena zasahuje vice mist nebo meni chovani
3. implementace
4. `code-review`
5. `completion-audit`, kdyz ma vystup jit klientovi nebo do produkce

Pozor na:

- tiche rozsirovani scope
- opravy popsane v chatu, ale nezapsane v souboru
- zmeny bez overeni realneho chovani

### Kdyz uzivatel zacina novy projekt

Pouzij:

1. `brief-builder`
2. `task-router`
3. podle typu projektu:
   - agent nebo bot -> `new-agent-project`
   - collector a dashboard -> `railway-collector-app`
   - ingest endpoint -> `fastapi-ingest-api`
4. `security-review`, pokud se pracuje s klici, loginem nebo uzivatelskymi daty

### Kdyz uzivatel debugguje

Pouzij:

1. `precision-mode`
2. pokud jde o Railway nebo env problemy -> `debug-railway-env`
3. pokud jde o DB -> `railway-db` nebo `db-migrate`
4. po oprave `code-review`
5. pred releasem `completion-audit`

### Kdyz uzivatel deployuje

Pouzij:

1. `code-review`
2. `security-review`
3. `railway-deploy`
4. pokud Railway nevzalo zmeny -> `railway-redeploy`
5. pokud app po deployi nevidi promenne -> `debug-railway-env`

### Kdyz uzivatel stavi knowledge base nebo AI trenera

Pouzij:

1. `brief-builder`
2. `yt-transcripts`, pokud je zdroj YouTube
3. `yt-rag`, pokud chce dotazovani nad obsahem
4. `yt-gpt-builder`, pokud chce soubory pro GPT nebo Assistant
5. `frontend-live-dashboard`, pokud chce prehled vysledku nebo prubehu

### Kdyz uzivatel resi sber a zobrazeni dat pro trading nebo monitoring

Pouzij:

1. `brief-builder`
2. `railway-collector-app`
3. `railway-db`
4. `frontend-live-dashboard`
5. `db-migrate` nebo `git-data-sync`, pokud je potreba presun nebo zaloha dat
6. `security-review` pred nasazenim

## Projektove mapy

### Mail agent

Typicke workflow:

1. `brief-builder`
2. `new-agent-project`
3. `telegram-bot-setup`
4. `security-review`
5. `code-review`
6. `railway-deploy`

Pouzij ve fazich:

- navrh workflow schvalovani odpovedi
- napojeni inboxu nebo API
- zavedeni KB a odpovedni logiky
- klientske upravy tone of voice nebo routing pravidel

### AI trener

Typicke workflow:

1. `brief-builder`
2. `yt-transcripts`
3. `yt-rag` nebo `yt-gpt-builder`
4. `frontend-live-dashboard`, pokud chces prubezny prehled
5. `code-review`
6. `railway-deploy`, pokud to jde ven

Pouzij ve fazich:

- sber a trideni zdrojoveho obsahu
- stavba knowledge base
- priprava dat pro trening nebo retrieval
- overeni, ze odpovedi sedi na zdroje

### Trading

Typicke workflow:

1. `brief-builder`
2. `railway-collector-app` nebo `fastapi-ingest-api`
3. `railway-db`
4. `frontend-live-dashboard`
5. `db-migrate`
6. `security-review`
7. `railway-deploy` nebo `railway-redeploy`

Pouzij ve fazich:

- ingest market dat
- lokalni collector -> Railway API -> PostgreSQL
- dashboard a polling
- obnova nebo presun historickych dat
- opravy env a runtime problemu

## Vystupni format

Vzdy vrat:

### Doporucene workflow

- **Faze projektu:**
- **Doporuceny postup:**
- **Skilly v poradi:**
- **Co udelat hned ted:**
- **Riziko / pozor na:**

## Priklady vstupu

- `Budu implementovat feedback od klienta do mail agenta`
- `Jdu rozjet novy projekt na AI trenera z YouTube transkriptu`
- `Resim, proc Railway po deployi nevidi DATABASE_URL`
- `Chci postavit trading collector s dashboardem`
- `Potrebuju zkontrolovat, jestli je tahle uprava fakt pripravena do produkce`
