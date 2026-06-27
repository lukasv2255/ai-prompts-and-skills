---
# Bez paths = načítá se vždy
---

# Styl kódu (Python)

- Preferuj jednoduché funkce před zbytečnými třídami — třída jen když drží stav
- Type hints u veřejných funkcí (signatury); vyhni se `Any`, buď konkrétní
- Maximální délka funkce: ~50 řádků — pokud je delší, rozděl ji
- Názvy proměnných a funkcí: popisné, anglicky, `snake_case`
- Žádná magická čísla — pojmenované konstanty (`UPPER_CASE` na úrovni modulu)
- Cesty kotvi přes `__file__` (`Path(__file__).resolve().parent`), ne relativně k CWD
- Loguj přes `logging`, ne `print()` v produkčním kódu

## Formátování

- Drž se PEP 8; formátuj přes `black` (řádek 88 znaků), importy `ruff`/`isort`
- Odsazení: 4 mezery
- Uvozovky: dvojité (`black` default)
- f-stringy pro interpolaci, ne `%` ani `.format()`

## Komentáře

- Komentuj **proč**, ne co
- Vyhni se komentářům, které jen opakují kód
- Docstring u veřejných funkcí a modulů (co dělá + nezřejmé vstupy/výstupy)
- TODO komentáře musí mít datum nebo ticket: `# TODO(2026-03-29): ...`
