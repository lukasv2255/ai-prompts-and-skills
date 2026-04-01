---
name: code-review
description: Detailní code review. Použij při kontrole implementace, před commitem, nebo když uživatel chce zkontrolovat kvalitu kódu.
allowed-tools: Read, Grep, Glob
---

# Code Review

## Správnost
- Logika odpovídá zadání
- Edge cases ošetřeny (None, prázdný list, nulové hodnoty)
- Error handling přítomen a smysluplný
- Async/await správně použit (pokud relevantní)

## Bezpečnost
- API klíče nejsou v kódu (musí být v .env)
- Vstupy od uživatele jsou validovány
- SQL/prompt injection rizika

## Kvalita kódu
- Žádný duplicitní kód
- Funkce dělají jednu věc
- Názvy jsou popisné
- Žádné `print()` v produkčním kódu — použij `logging`

## Výstup

Uveď konkrétně: `soubor:řádek` + popis + navrhovaný fix.
Začni tím nejkritičtějším. Zmiň i co je dobře napsáno.
