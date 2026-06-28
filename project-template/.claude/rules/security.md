---
paths:
  - "**/server.py"
  - "**/db.py"
  - "**/api/**"
  - "**/auth/**"
---

# Bezpečnostní pravidla

## Absolutní zákazy

- Nikdy necommituj `.env` soubory
- Nikdy neloguj hesla, tokeny ani PII (jména, e-maily, GPS, ID účtů)
- Nikdy nepoužívej `eval()` / `exec()` na uživatelském vstupu
- Nikdy nevkládej uživatelský vstup přímo do SQL — vždy parametrizované dotazy

## Auth a sessions

- Kontroluj autentizaci PŘED každou DB operací
- Kontroluj autorizaci (ownership) na každém endpointu s uživatelskými daty
- Session cookies: podepsané, `httpOnly`, `secure` flag v produkci
- Omezené role (demo, read-only) zamykej i na backendu, ne jen v UI

## Tokeny třetích stran (OAuth)

- Access/refresh tokeny jen v DB, nikdy do gitu ani logů
- Ošetři refresh — access tokeny expirují

## Co kontrolovat

1. SQL injection → parametrizované dotazy
2. Únik tajemství → `.env`, žádné klíče v kódu ani logu
3. Broken auth → platnost a scope session/tokenu
4. Citlivá data → minimalizuj, co odchází do třetích stran (včetně AI)
5. Misconfiguration → debug mode vypnutý v produkci
