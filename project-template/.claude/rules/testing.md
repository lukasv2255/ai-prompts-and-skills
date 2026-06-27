---
# Bez paths = načítá se vždy
---

# Pravidla pro testy

- Piš testy **před** nebo **zároveň** s implementací (ne po)
- Každá nová funkce nebo fix musí mít odpovídající test
- Framework: `pytest`. Testy v `tests/`, soubory `test_*.py`, funkce `test_*`
- Pojmenování vyjadřuje chování: `test_<co>_<za_jakych_podminek>`
  (např. `test_threshold_falls_back_when_no_record`)

## Co testovat

- Happy path (úspěšný případ)
- Edge cases (prázdné vstupy, nulové a hraniční hodnoty, chybějící data)
- Error handling (co se stane při chybě)

## Co netestovat

- Interní implementační detaily
- Knihovní a frameworkové funkce samy o sobě

## Databáze v testech

- Testy běží proti **reálné lokální DB** (typicky SQLite), ne proti mockům
- Použij dočasnou DB (`tmp_path` fixture) nebo si po sobě data ukliď
- Nikdy nezapisuj do produkční DB z testů

## Spouštění

- `pytest` z kořene projektu (z venv: `.venv/bin/pytest`)

## Pokrytí

- Kritické moduly (výpočty, auth, datové migrace): vysoké pokrytí
- Ostatní: rozumné pokrytí, ne za každou cenu 100 %
