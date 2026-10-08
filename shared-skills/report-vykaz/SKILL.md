---
name: report-vykaz
description: >
  Postaví z pracovního výkazu (hodiny po blocích + poznámky) HTML přehled pro klienta:
  každý blok má koláčový graf „% hotovo“ a tři sekce Hotové / Zbývá / Budoucí projekty,
  drobné položky jdou do tabulky Ostatní. Výstup je HTML i PDF na 2 strany A4.
  Druhý člen rodiny reportů, sdílí s `report-na-web` brand kity (`../report-na-web/brands/`).
  Servíruje na localhostu.

  Použij kdykoliv uživatel říká:
  - "udělej z výkazu report / přehled pro klienta"
  - "výkaz po blocích s grafy"
  - "co je hotové, co zbývá, budoucí projekty — za měsíc"
  - "/report-vykaz <zdroj> [--brand <slug>]"
---

# report-vykaz — výkaz po blocích s grafy

Rodina reportů:
- `report-na-web` — referenční report s bočním panelem a sekcemi (rozbor, stav projektu).
- `report-vykaz` — měsíční výkaz pro klienta: bloky práce, % hotovo, co zbývá, co z toho plyne.

Cíl: klient na jedné stránce vidí, **za co platí, co už má hotové a co ho čeká**.
Není to faktura ani deník úkonů.

---

## Tvrdá pravidla věrnosti zdroji

1. **Procento do grafu dodává uživatel.** Ze zdrojů ho nedopočítávej ani neodhaduj.
   Blok bez procenta nemá graf (typicky meetingy: tam se nic „nedokončuje“) a jde do Ostatních.
2. **Zbývá a Budoucí projekty jen ze zdroje / od uživatele.** Žádné vlastní návrhy
   dalších kroků. Když uživatel u bloku nic neřekne, zeptej se, nevymýšlej.
3. **Čísla (hodiny, počty, průměry) přebírej doslova.** Když nějaké číslo vzniklo tvým
   výpočtem (např. součet hodin v Ostatních), řekni to v odpovědi.
4. Když uživatel diktuje heslovitě, přepiš to do celých vět, ale bez nových tvrzení.
   Opravy názvů (překlepy produktů) a změny slov s jiným významem v odpovědi nahlas zmiň.

---

## Struktura stránky

- **Hlavička:** gradient `--primary → --sidebar`, logo značky (volitelně), nadpis
  `Podrobný pracovní výkaz – <měsíc>` (`{{DOC_TITLE}}`) a pod ním jméno autora
  (`{{AUTOR}}`, menším písmem). **Žádná oslovení ani úvodní věty** typu
  „Výkaz odsouhlasuju“; ty patří do mailu, ne do reportu.
- **Blok** = karta:
  - `<h2>N) Název bloku (XX h)</h2>`: **hodiny v závorce za nadpisem, bez sazeb.**
    Sazby a částky do reportu nepatří, pokud je uživatel výslovně nechce.
  - vlevo graf `% hotovo` (bez legendy, všechny grafy stejně velké), vpravo tři sekce `Hotové` / `Zbývá` / `Budoucí projekty`.
  - Hotové: věcně, co vzniklo. Konkrétní dílčí výsledek uveď tučným štítkem:
    `<strong>Dílčí projekt:</strong>` (konkrétní zakázka uvnitř bloku) nebo
    `<strong>Dílčí výstup:</strong>` (zjištění, číslo, měření).
  - Zbývá: když nic, napiš „Nic.“ (nevynechávat sekci).
- **Ostatní** = tabulka `položka | hodiny`, bez grafu. Patří sem meetingy a drobnosti.
  Do nadpisu součet hodin.
- **Bez závěrečného shrnutí** (jednorázové vs. dál použitelné, poznámky o nástrojích
  apod.), pokud ho uživatel výslovně nechce. To je text do průvodního mailu.

---

## Postup

1. **Přečti zdroj** (výkaz, CSV, mail, poznámky) a rozděl práci do bloků podle hodin.
   Ke každému bloku si od uživatele vyžádej: procento, co zbývá, budoucí projekty.
   Ptej se najednou na všechny bloky, ne po jednom.
2. **Zkopíruj `template.html`** do složky reportu jako `vykaz-<mesic>.html`
   (měsíc česky bez diakritiky: `vykaz-zari.html`). Stejný název dostane i PDF.
3. **Brand kit:** obsahem `../report-na-web/brands/<slug>.css` (bez `--brand` = `ai-brand.css`)
   nahraď blok `/* BRAND:START */ … /* BRAND:END */`. Když projekt má vlastní
   `brand-kit/assets/*-logo-white.svg`, zkopíruj ho vedle reportu a vlož do `{{LOGO}}`
   jako `<img src="…" alt="…">`. Jinak `{{LOGO}}` smaž.
4. **Grafy:** sepiš `grafy.json` (formát v hlavičce `grafy.py`) a spusť
   ```bash
   python3 ~/ai-prompts-and-skills/shared-skills/report-vykaz/grafy.py <složka>/grafy.json --barva "<--primary značky>"
   ```
   PNG vzniknou vedle JSONu. Zdrojové grafy jinde v projektu nepřepisuj.
5. **Vyplň bloky** podle `<!-- BLOK -->` a `<!-- OSTATNÍ -->` v šabloně, `{{TITLE}}`,
   `{{DOC_TITLE}}` a `{{AUTOR}}`.
6. **Naservíruj:**
   ```bash
   ~/ai-prompts-and-skills/shared-skills/_shared/serve.sh <složka> vykaz-<mesic>.html
   ```
7. **PDF** z běžícího localhostu (ne file://, jinak chybí fonty a obrázky):
   ```bash
   python3 ~/ai-prompts-and-skills/shared-skills/report-vykaz/pdf.py <url z kroku 6> <složka>/vykaz-<mesic>.pdf
   ```
   Skript vypíše počet stran. Cíl jsou **2 strany A4**; tiskové styly v šabloně
   (`@media print`) jsou na to zhuštěné. Když vyjde víc, zhusti tiskové styly dál,
   obsah nezkracuj.
8. Pošli oba odkazy: `…/vykaz-<mesic>.html` a `…/vykaz-<mesic>.pdf`.
   Po každé úpravě HTML vygeneruj PDF znovu, ať se nerozjedou.

## Mail vs. report

Report se často posílá spolu s mailem. Když uživatel chce i text do mailu, je to
samostatný plain text v code blocku (bez markdown bulletů) a obsahuje to, co v reportu
není: odsouhlasení výkazu, sazby, souhrn, poznámky.

## NDA a citlivá data

Report zůstává lokálně (localhost). Do tohohle skillu (veřejné repo) nikdy nekopíruj
obsah konkrétních výkazů ani klientské texty, jen obecná pravidla.
