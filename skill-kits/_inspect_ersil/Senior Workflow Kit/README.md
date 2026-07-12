# Skills — jak je používat za sebou

Tahle sada skillů tvoří jeden pracovní postup: od syrového zadání k ověřenému, klientsky bezpečnému výstupu. Dají se použít jednotlivě, ale hlavní hodnota je v pořadí — každý krok opravuje slabinu předchozího.

## Rychlá cesta: `/launch-campaign`

Pro launch kampaň produktu/služby z neúplných podkladů (pár assetů, neschválený rozpočet, nepotvrzená cílovka) spusť rovnou:

```
/launch-campaign <popis produktu a co k tomu máš>
```

Uvnitř proběhne celá sekvence níže automaticky — brief, routing, target lock, plán agentů se schválením, spuštění, dva nezávislé audity, zápis finálního souboru. Použij tohle, pokud nechceš řídit kroky ručně.

Pro cokoliv jiného než launch kampaně (kód, research, jednorázový obsah) skládej kroky ručně podle tabulky níže.

## Pořadí kroků (ruční skládání)

| # | Skill | Co dělá | Kdy ho přeskočit |
|---|---|---|---|
| 1 | `/brief-builder` | Ze zmatených poznámek/zadání udělá pracovní brief: cíl, cílovka, podklady, omezení, rizika, **domněnky jasně oddělené od faktů**, otevřená otázka | Nikdy nepřeskakovat, pokud je vstup nejasný, emocionální nebo neúplný — tohle je základ, na kterém stojí všechno další |
| 2 | `/task-router` | Rozdělí práci na role (scout/builder/auditor) a přidělí jim modely a effort úsporně — ne vždy nejsilnější model | Přeskoč u triviálních úkolů bez rizika/nejasnosti, kde stačí jeden model |
| 3 | `/precision-mode` | Před tvorbou ukáže **target lock**: cíl, acceptance criteria, co je neověřené — čekací bod, kde uživatel może opravit směr, než se utratí práce | Přeskoč jen u nízkorizikových, triviálních úkolů |
| 4 | `/agent-chain` | Napíše přesné prompty pro scout/builder/auditor, formát předávání a stop podmínky. **Ukazuje plán, čeká na schválení, teprve pak spouští agenty** | Přeskoč, pokud stačí jeden model bez dělby práce |
| 5 | *(spuštění)* | Scout sbírá fakta se zdroji → builder staví výstup jen z potvrzených vstupů, s explicitním seznamem "tohle netvrdit" → auditor nezávisle kontroluje proti kritériím z kroku 3 | — |
| 6 | `/completion-audit` | **Druhý, jinak zaměřený** audit — nekontroluje stejná kritéria znovu, ale loví domněnky vydávané za fakt, vynechaná rizika a to, jestli opravy z kroku 5 skutečně existují v souboru, ne jen v chatu | Přeskoč jen když je výstup skutečně nízké riziko |
| 7 | `/method-capture` | Když se postup osvědčí, promění ho v opakovatelný skill/slash příkaz pro příště | Použij jen když chceš postup zopakovat na jiném zadání |

## Proč na pořadí záleží

- **Brief před routerem** — nedává smysl přidělovat modely úkolu, který ještě nikdo pořádně nedefinoval.
- **Target lock před agent-chainem** — bez schválených acceptance criteria nemá auditor v kroku 6 proti čemu kontrolovat.
- **Plán agentů se ukazuje před spuštěním** — drahé kroky (více spawnutých agentů) se nespouští naslepo.
- **Dva audity, ne jeden** — první kontroluje proti explicitním kritériím (rychlé, formální), druhý aktivně hledá to, co první typicky přehlédne (domněnky vydávané za fakt, nepersistované opravy). Jeden audit tohle spolehlivě nechytí.
- **Method-capture je poslední** — zachycuje postup až poté, co se ověřil v praxi, ne předem jako teorii.

## Seznam skillů v této složce

- **brief-builder** — vágní zadání → přesný pracovní brief
- **task-router** — volba modelu/efortu/workflow úsporně podle rizika a nejasnosti
- **precision-mode** — senior operator smyčka pro těžké/nejednoznačné úkoly (target lock → evidence → pressure test → proof → brief)
- **agent-chain** — návrh multi-agent workflow se scoutem, builderem a nezávislým auditorem
- **completion-audit** — nezávislé ověření, že je práce skutečně hotová
- **method-capture** — proměna osvědčeného postupu v opakovatelný skill
- **launch-campaign** — zabalená verze celé sekvence 1–6 pro launch kampaně, jedno zadání

## Pravidlo, které platí napříč vším

Žádná domněnka nesmí v konečném výstupu vypadat jako fakt. Co není potvrzené vstupem, musí zůstat viditelně označené jako předpoklad — od briefu až po finální soubor.
