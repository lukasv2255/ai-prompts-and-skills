---
name: railway-redeploy
description: Vynutí okamžitý redeploy projektu na Railway. Použij kdykoliv uživatel říká "redeploy", "znovu nasaď", "force deploy", "railway up", "nic se nezměnilo na Railway", nebo když se zdá že Railway nenatáhlo poslední změny z Gitu.
---

# Railway Redeploy

Vynutí redeploy aktuálního projektu na Railway — obejde automatický Git trigger a nahraje aktuální stav přímo.

## DŮLEŽITÉ: Dva kroky jsou nutné

`railway up` pouze builduje Docker image — **NESPUSTÍ nový container automaticky**.
Po buildu je nutné vždy zavolat `railway redeploy --yes`.

## Postup

1. Zkontroluj že jsi ve správném adresáři projektu
2. Build + upload (streamuje logy, čeká na dokončení):

```bash
railway up --ci
```

3. Po dokončení buildu restartuj container s novým image:

```bash
railway redeploy --yes
```

4. Počkej ~60 sekund a ověř logy:

```bash
railway logs 2>&1 | tail -10
```

5. Potvrď uživateli — v logu hledej `Starting Container` s novým timestampem.

## Poznámky

- `--ci` = streamuje build logy a čeká na dokončení (vidíš případné chyby)
- `--detach` = jen spustí build a vrátí URL, nevidíš výsledek
- `railway redeploy --yes` = restartuje service s posledním buildem (přeskočí confirm dialog)
- Pokud projekt není nalinkován: `railway link`
