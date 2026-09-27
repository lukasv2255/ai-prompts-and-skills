---
name: tahak
description: >
  Tahák na schůzku jako HTML: očíslované body (KPI) a pod každým rozbalovací
  nabídka s podrobnostmi. Uživatel pak v chatu diktuje „přidej k N: …" a skill
  jeho text vloží do nabídky u bodu N — jen mírně zkrácený, s opravenými chybami
  a diakritikou. Servíruje na localhostu.

  Použij kdykoliv uživatel říká:
  - "udělej mi tahák na meeting / schůzku s ..."
  - "přidej k 2: ..." / "ad 1: ..." (u rozpracovaného taháku)
  - "KPI 4: ..." / "nový bod: ..." / "ad úvod: ..." / "ad průběžně: ..."
  - "/tahak <téma> [účastníci]"
---

# tahak — tahák na schůzku

Stránka má nadpis, řádek s účastníky a tři sekce podle průběhu schůzky:

| Sekce | Co v ní je | Karta |
|---|---|---|
| **Úvod** | jak schůzku otevřu, komu nechám slovo, o co si řeknu (čas na dotazy) | pomlčka `—` místo čísla |
| **Průběžně** | co zmíním, když přijde řeč na dané téma (reakce na mail, postoj) | pomlčka `—` |
| **Závěr** | moje dotazy, očíslované KPI od 1 | číslo |

Každá karta má jednu větu (co chci, na co se ptám) a pod ní sbalenou nabídku
**Podrobnosti** s odrážkami. Nic dalšího. Sekci, do které uživatel nic nedal,
vynech celou.

Layout je hotový v `template.html` (design systém projektu AI-brand: DM Serif
Display / Outfit / JetBrains Mono, béžové pozadí, bez stínů, mobil pod 640 px).

## Tvrdá pravidla (nikdy neporušit)

1. **Obsah je jen od uživatele.** Nepřidávej vlastní analýzu, výhody/nevýhody,
   doporučení, otázky ani pole na odpovědi, pokud o ně výslovně neřekne.
   I když v projektu najdeš relevantní podklady, do taháku je sám nedávej.
2. **Text uživatele zachovej.** Jen mírně zkrať (vyhoď vatu a opakování),
   oprav překlepy, diakritiku, interpunkci a velká písmena u jmen
   (Reditas, SpringWalk, Evolio). Nepřeformulovávej smysl, nepřidávej fakta.
3. **Delší souvětí rozděl do více odrážek**, jedna myšlenka = jedna odrážka.
   Pořadí zachovej.
4. **Anglicismy přelož**, jen když je český ekvivalent jasný
   („optional" → „volitelné"). Odborné pojmy nech.

## Postup

### Nový tahák

1. Zjisti z požadavku titul, účastníky a úvodní body. Chybí-li účastníci,
   řádek `.who` vynech.
2. Zkopíruj `template.html` do projektu, kterého se schůzka týká, typicky
   `<projekt>/docs/…/meeting-<kdo>/tahak-<tema>.html`. Nahraď `{{TITUL}}`,
   `{{UCASTNICI}}` a vzorové karty (`{{UVOD}}`, `{{PRUBEZNE}}`, `{{BOD}}`)
   skutečnými body. Body, které uživatel jen vyjmenuje bez sekce, patří do Závěru.
3. Bod bez podrobností má v nabídce `<p class="empty">Zatím nic.</p>`.
4. Naservíruj přes `~/ai-prompts-and-skills/shared-skills/_shared/serve.sh <složka> <soubor>`
   a pošli URL.

### „Přidej k N: …" / „ad N: …" / „ad úvod: …" / „ad průběžně: …"

- Najdi kartu `.kpi` s číslem N, nebo kartu v sekci Úvod / Průběžně.
  Když sekce ještě neexistuje, vlož ji na její místo (Úvod → Průběžně → Závěr).
  Větu na kartu (`.what`) udělej krátce z textu uživatele. Pokud je v nabídce `.empty`, nahraď ho `<ul>`.
- Text přidej na **konec** seznamu `<ul>` jako nové `<li>` (podle pravidel 2–3).
- Nic jiného v souboru neměň.

### „KPI N: <nadpis>, ad N: …" / nový bod

- Přidej novou kartu `.kpi` na konec Závěru (číslo = poslední + 1, nebo jak řekne uživatel).
- Nadpis = krátká věta z textu uživatele, zbytek jde do nabídky.

## Odpověď v chatu

Krátce: co přibylo (vypiš vložené odrážky, ať je vidět úprava textu) a URL.
Server už běží, stačí obnovit stránku.
