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

### KROK 1 — Git commit + push (VŽDY povinný)

Railway deployuje výhradně z Gitu. Bez pushe se změny nenasadí.

```bash
git status
git diff --stat
```

Pokud jsou uncommitted změny nebo nepushnuté commity:

```bash
git add <soubory>
git commit -m "popis změn"
git push
```

Nikdy nepřeskakuj tento krok. `railway redeploy` bez pushe nasadí **starý** commit.

### KROK 2 — Zkontroluj správný adresář projektu

### KROK 3 — Build + upload

```bash
railway up --ci
```

### KROK 4 — Restart containeru s novým image

```bash
railway redeploy --yes
```

### KROK 5 — Ověř logy

```bash
railway logs 2>&1 | tail -10
```

Potvrď uživateli — v logu hledej `Starting Container` s novým timestampem.

## Poznámky

- `--ci` = streamuje build logy a čeká na dokončení (vidíš případné chyby)
- `--detach` = jen spustí build a vrátí URL, nevidíš výsledek
- `railway redeploy --yes` = restartuje service s posledním buildem (přeskočí confirm dialog)
- Pokud projekt není nalinkován: `railway link`
