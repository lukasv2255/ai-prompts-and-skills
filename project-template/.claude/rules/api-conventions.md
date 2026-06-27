---
paths:
  - "**/server.py"
  - "**/api/**"
  - "**/routes/**"
  - "**/handlers/**"
---

# API konvence (FastAPI)

## Response shape

- Vracej Pydantic modely nebo `dict` — FastAPI je zserializuje do JSON
- Drž jednotný tvar napříč endpointy
- Chyby hlas přes `HTTPException`, ne vlastní ad-hoc `{error: ...}` v každém handleru

## Validace

- Vstupy validuj Pydantic modely (request body) a typovanými parametry cesty/query
- Nevalidní vstup → FastAPI vrátí `422` automaticky, nevyrábej z toho `500`
- Nikdy nevěř vstupu bez validace

## Chybové kódy

- `400` — bad request
- `401` — unauthorized (není přihlášen)
- `403` — forbidden (nemá oprávnění / omezená role)
- `404` — not found
- `409` — conflict (duplicita)
- `422` — validační chyba (FastAPI default)
- `500` — server error

## Bezpečnost

- Nikdy neexponuj stack traces ani interní chyby klientovi
- Parametrizované SQL dotazy (žádná konkatenace vstupu)
- Auth a ownership kontroluj na začátku handleru, před DB operací
