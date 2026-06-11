# Skill: otestuj

Spustí testy preview stránek, Railway odkazů a HTML mailů. Defaultně testuje jen záznamy se stavem `ready`.

## Použití

- `otestuj` — testuje preview + railway + maily, jen stav `ready`
- `otestuj vše` — testuje preview + railway + maily, všechny záznamy
- `otestuj preview` — testuje jen preview stránky
- `otestuj maily` — testuje jen HTML maily
- `otestuj railway` — testuje jen Railway URL

## Co udělej

### otestuj (default — jen ready)

1. Zjisti slugy leadů se stavem `ready` z DB + CSV
2. Spusť všechny tři testy a filtruj výsledky jen na ready slugy:

```
cd {PROJECT_ROOT}
python3 tests/test_previews.py
python3 tests/test_mails.py
python3 tests/test_railway.py --count 50
```

Zobraz jen řádky které patří ready leadům. Reportuj souhrnně.

### otestuj vše

Spusť všechny tři testy bez filtru a zobraz souhrnné výsledky.

### otestuj preview
```
cd {PROJECT_ROOT}
python3 tests/test_previews.py
```
Vyhodnoť výsledky. Waiting záznamy bez preview jsou OK.

### otestuj maily
```
cd {PROJECT_ROOT}
python3 tests/test_mails.py
```
Vyhodnoť výsledky. `waiting` bez Railway linku jsou OK. `ready to deploy` nebo `ready` bez linku jsou problém.

### otestuj railway
```
cd {PROJECT_ROOT}
python3 tests/test_railway.py --count 50
```
Testuje Railway URL. Filtruj jen `ready` záznamy pokud není řečeno jinak.

## Interpretace výsledků

- `⚠MAPA` — preview nemá Google Maps embed → re-render nebo znovu zpracovat
- `⚠HERO=SVG_BEZ_FIXU` — hero má prázdný SVG místo fotky → zkontroluj verzi template.html
- `⚠PH=N` (N≥4) — příliš mnoho placeholderů v galerii → web má velmi málo fotek
- `⚠CHYBÍ_LINK` u ready to deploy/ready → mail bez preview URL → smaž mail a znovu spusť dashboard
- `⚠HTTP=404` — preview není nasazeno na Railway → potřeba redeploy
- `⚠HTTP=0` — web nedostupný nebo timeout
- `⚠NÁZEV_NESEDÍ` — AI vygenerovala jiný název než Railway stránka → posouď zda je to problém
