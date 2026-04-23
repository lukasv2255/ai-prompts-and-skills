# Šablona promptu pro autonomní úkol

Použij když chceš aby agent pracoval samostatně bez přerušení.

---

## Šablona

```
Úkol: [CO MÁ BÝT HOTOVÉ]

Kritéria hotovo:
- [konkrétní chování 1]
- [konkrétní chování 2]

Scénáře k otestování:
- S1: udělej [X], očekávám [Y]
- S2: udělej [X], očekávám [Y]

Postup:
1. Přečti tasks/lessons.md
2. Analyzuj co je rozbité — projdi relevantní soubory sám
3. Opravuj iterativně — po každé funkční změně git commit
4. Testuj scénáře přes Playwright po každé změně
5. Na konci shrň co jsi změnil a proč

Nepřerušuj práci — nečekej na moje potvrzení.
Pokud narazíš na blocker který nemůžeš vyřešit sám, teprve tehdy se zeptej.
```

---

## Scénáře pro web/dashboard

```
S — Refresh persistence
  1. Otevři stránku
  2. Screenshot
  3. Reload (F5)
  4. Screenshot
  Očekávám: identické tlačítka, texty a emoji v obou screenshots

S — Prázdný stav
  1. Otevři stránku bez dat
  2. Počkej 30s
  3. Screenshot
  Očekávám: smysluplný fallback stav, žádná prázdná karta

S — Polling flicker
  1. Otevři stránku
  2. Screenshot každé 2s po dobu 10s
  Očekávám: karta vždy ve stejném stavu, žádné probliknutí

S — Side effect po akci
  1. Klikni na tlačítko
  2. Zkontroluj logy
  Očekávám: backend call proběhl (Telegram, DB, API...)
```
