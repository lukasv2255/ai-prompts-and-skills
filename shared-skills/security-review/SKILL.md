---
name: security-review
description: Bezpečnostní audit kódu. Použij před deploymenty na Railway, při práci s API klíči, nebo když kód pracuje s uživatelskými vstupy.
allowed-tools: Read, Grep, Glob
---

# Security Review

## API klíče & secrets
- Hledej hardcoded API klíče, tokeny, hesla v kódu
- Zkontroluj .gitignore — je tam .env?

## Vstupy
- Uživatelské vstupy do Telegram botu — jsou validovány?
- Prompt injection v AI callech — uživatel může manipulovat system prompt?

## Závislosti
- Zastaralé nebo zranitelné balíčky (zkontroluj requirements.txt)

## Deployment (Railway)
- Env proměnné nastaveny v Railway, ne v kódu
- Debug mode vypnutý v produkci

## Výstup

Pro každý nález: **Závažnost** (Kritická/Vysoká/Střední/Nízká) + soubor:řádek + popis + fix.
