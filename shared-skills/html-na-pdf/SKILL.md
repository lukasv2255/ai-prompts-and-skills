---
name: html-na-pdf
description: >
  Vyrobí PDF z libovolné HTML stránky (report, výkaz, nabídka, tahák, prezentace)
  přes headless Chrome: stránku naservíruje na localhostu, vytiskne ji do PDF
  a vypíše počet stran. Obecný nástroj pro všechny projekty; jednorázové PDF skripty
  v projektech se nepíšou. Vzhled PDF řídí tiskové styly stránky (`@media print`, `@page`).
  Použij kdykoliv uživatel říká:
  - "udělej z toho PDF" / "vyexportuj report do PDF"
  - "potřebuju PDF verzi nabídky / výkazu / taháku"
  - "kolik stran má to PDF" / "zhusti to na 2 strany"
  - "/html-na-pdf <soubor.html> [výstup.pdf]"
---

# html-na-pdf — PDF z HTML stránky

Jedno místo, kudy vzniká PDF z HTML. Volají ho i jiné skilly (`report-vykaz`).

## Postup

1. **Naservíruj složku se stránkou** (ne `file://` — jinak chybí fonty a obrázky):
   ```bash
   ~/ai-prompts-and-skills/shared-skills/_shared/serve.sh <složka> <soubor.html>
   ```
   Skript vypíše URL (jedna složka = jeden stálý port).
2. **Vytiskni do PDF:**
   ```bash
   python3 ~/ai-prompts-and-skills/shared-skills/html-na-pdf/pdf.py <url z kroku 1> <výstup.pdf>
   ```
   Výchozí výstup je vedle HTML se stejným jménem (`report.html` → `report.pdf`).
   Skript vypíše počet stran (s `pypdf`, jinak jen velikost).
3. **Stránkování a vzhled** se ladí v HTML, ne ve skriptu:
   - `@page { size: A4; margin: … }` (na šířku: `size: A4 landscape`),
   - `@media print { … }` — skrýt navigaci, zhustit písmo a mezery, `break-inside: avoid`
     u karet a tabulek, `print-color-adjust: exact` pro barevná pozadí.
   Když má PDF vyjít na daný počet stran a nevychází, zhusti tiskové styly, obsah nezkracuj.
4. Pošli cestu k PDF a počet stran.

## Pravidla

- PDF je výstup — ukládá se k dokumentu (do `docs/…` projektu), skript zůstává tady.
- Do projektu se nepíše vlastní PDF generátor (WeasyPrint, kopie `pdf.py`…); co skript
  neumí, se doplní sem pro všechny.
- Vyžaduje nainstalovaný Google Chrome (Mac i Windows; na Linuxu `google-chrome`/`chromium`).
