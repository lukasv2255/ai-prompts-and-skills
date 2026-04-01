---
name: railway-redeploy
description: Vynutí okamžitý redeploy projektu na Railway pomocí `railway up --detach`. Použij kdykoliv uživatel říká "redeploy", "znovu nasaď", "force deploy", "railway up", "nic se nezměnilo na Railway", nebo když se zdá že Railway nenatáhlo poslední změny z Gitu.
---

# Railway Redeploy

Vynutí redeploy aktuálního projektu na Railway — obejde automatický Git trigger a nahraje aktuální stav přímo.

## Postup

1. Zkontroluj že jsi ve správném adresáři projektu (kde je `.railway/` složka nebo `railway.json`)
2. Spusť redeploy:

```bash
"C:/Users/tommy/railway.exe" up --detach
```

3. Počkej ~90 sekund a ověř logy:

```bash
"C:/Users/tommy/railway.exe" logs 2>&1 | tail -15
```

4. Potvrď uživateli že nový kód běží — v lozích hledej startup hlášky odpovídající aktuální verzi kódu.

## Poznámky

- `--detach` = nečeká na dokončení buildu, jen spustí a vrátí URL build logů
- Pokud projekt není nalinkován, nejdřív spusť: `"C:/Users/tommy/railway.exe" link`
- Railway CLI je na `C:/Users/tommy/railway.exe`
