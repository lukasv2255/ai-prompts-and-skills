---
name: report
description: >
  Postaví z podkladového (raw) dokumentu čitelný HTML report s pevným bočním panelem
  vlevo a sekcemi vpravo. Strohá referenční verze, ne dlouhý souvislý text. Technické
  věci schované do sbalených rolet přímo v sekci. Přepínač brand kitu. Servíruje na
  localhostu.

  Použij kdykoliv uživatel říká:
  - "udělej z toho report / HTML report"
  - "přepiš ten dokument do reportu"
  - "report pro <někoho> ze <souboru>"
  - "/report <zdroj> [--brand <slug>]"
---

# report — HTML report s bočním panelem

Cíl: z raw dokumentu (markdown, poznámky, existující report) udělat **referenční
stránku**, kde příjemce skočí na sekci, přečte jednořádkový závěr a případně rozklikne
detail. Není to esej ke čtení odshora dolů.

Layout je hotový v `template.html`: fixní boční panel (titul + datum/autor + navigace
na sekce) a obsah vpravo. Na mobilu se panel sbalí nad obsah.

**Report se chová jako prezentace:** vidět je vždy jen jedna sekce. Ostatní jsou skryté,
ne odscrollované. Pravidla jsou níže v „Prezentační režim".

---

## Tvrdá pravidla věrnosti zdroji (nikdy neporušit)

Tohle je důvod, proč skill existuje. Report **jen přeskládá a zestruční** to, co je
v raw dokumentu. Nedomýšlí.

1. **Žádné závěry ani návrhy dalších cest**, které nejsou **explicitně** v raw zdroji.
2. **Žádné předjímání pokračování projektu.** Když projekt ještě není rozhodnutý,
   report nesmí naznačovat „takhle to bude dál", doporučené varianty apod.
3. **Žádné časové odhady** („půl dne", „pár dní", „týdny provozu"), pokud ten odhad
   **není doslova v raw dokumentu**. Skill si čísla nevymýšlí ani neodhaduje.
4. Chybí-li ve zdroji závěr, v reportu **prostě není** — nedovozovat ho z okolí.

Když si nejsi jistý, jestli je tvrzení ve zdroji: **vynech ho**, neriskuj domýšlení.

---

## Pravidla stylu (strohá verze)

- **Každá sekce začíná jednořádkovým závěrem** (`<p class="lead">`), ne odstavcem rozjezdu.
- Dál krátké odrážky nebo tabulka. Bez vysvětlování „proč", bez marketingového tónu.
- **Bez hovorových výrazů.** („funguju", „nejpalčivější", „sype se", „nejmíň", „navrhuju" → ven.)
- **Bez obrazných sloves místo věcných.** „prompt bydlí" → je uložený; „sahat na prompt" →
  měnit ho; „sáhnout na spis" → vyžádat si ze spisu; „páka na náklady" → ovlivňuje náklady.
- **Bez em dashů (—).** Místo nich tečka, čárka nebo dvojtečka. (Číselné rozsahy piš „7 až 28".)
- **Bez přivlastňovacích zájmen ve srovnáních.** „jejich generování", „jejich rozhraní",
  „naše sazba" → působí hovorově a vůči druhé straně nezdvořile. Pojmenuj stranu konkrétně
  (Evolio, AVE Soft, kancelář), nebo větu přeformuluj tak, aby zájmeno nepotřebovala.
- **Bez hodnotících obratů typu „daní je", „výhodou je", „za cenu toho, že".** Uveď rovnou
  fakt, ne jeho hodnocení.
- **Bez technického žargonu v hlavním textu.** Anglicismy a názvy z implementace
  („dashboard", „endpoint", „polling") patří do sbalené rolety, ne do věty pro příjemce.
  V textu je nahraď českým popisem toho, co ta věc dělá („dashboard" → „přehled").
- **Callout (`div.note`) je jedna až dvě věty.** Pojmenuj věc a co je potřeba rozhodnout.
  Nerozvádět zdůvodnění, důsledky ani „jinak se stane to a to" — čtenář si to domyslí sám.
- **Stavy jako chipy** (`<span class="chip">`), ne věty. Strukturovaná fakta do tabulek.
- Výjimka z „strohosti": pokud uživatel řekne, že některá kapitola má být **stejně
  podrobná jako raw** (typicky rozbor variant), tu nech plný detail ze zdroje.

## Prezentační režim (výchozí chování)

Report není dlouhá stránka ke scrollování. **Zobrazuje se vždy právě jedna sekce**,
zbytek je `display:none`. Když je otevřený Krok 0, na obrazovce není Východisko ani nic
jiného. Logika je hotová v `template.html`, nepřepisuj ji:

- klik v bočním panelu **přepne** sekci, nescrolluje na ni,
- pod obsahem je lišta `div.steps` s **← Zpět / Dál →** a počítadlem `2 / 8`,
- šipky vlevo/vpravo a PageUp/PageDown přepínají taky,
- odkazy uvnitř textu (`<a href="#krok0">`) přepnou sekci, ne skočí do prázdna,
- URL drží hash (`#krok0`), takže odkaz otevře report rovnou na té sekci,
- do tisku (`Cmd+P`) jde **celý** report se všemi sekcemi, ne jen otevřená.

Kvůli tomu má sekce nést **celý svůj kontext**: čtenář nevidí, co bylo o obrazovku výš.

## Bez oslovení příjemce

V panelu **není „Pro <jméno>"** a není nikde jinde v dokumentu. Příjemce ví, že to dostal.
`{{META}}` je jen **datum · autor**. Titul (`{{DOC_TITLE}}`) pojmenovává **téma**
(„AI automatizace"), ne vztah k příjemci („Report pro Tomáše").

## Technické věci do sbalené rolety

Endpointy, názvy metod, kód, ID, session/cookies, launchd apod. **nemazat, ale schovat**
do `<details class="tech">` — sbalené defaultně, **přímo v sekci, kam patří**:

```html
<details class="tech"><summary>Technická poznámka</summary><div class="body">
  <p>… technický detail …</p>
</div></details>
```

---

## Postup stavby

1. **Přečti raw zdroj** a rozsekej ho na 3–6 sekcí. Sekce jsou **substantiva** (Možnosti
   řešení, Hotovo, Technické provedení, Otevřené otázky…). Když je sekcí moc, slučuj
   příbuzné (typicky „Hotovo + Zodpovězeno", „Otevřené otázky + Další kroky",
   „Kapacita + Generování → Technické provedení").
2. **Zkopíruj `template.html`** do cílové složky (vedle zdroje) jako
   `<slug>-report.html`.
3. **Brand kit (přepínač):** vezmi `brands/<slug>.css` (bez `--brand` = `ai-brand.css`)
   a jeho obsahem nahraď blok mezi `/* BRAND:START */` a `/* BRAND:END */` v šabloně.
   Seznam a návod na přidání značky: `brands/README.md`.
4. **Vyplň placeholdery:**
   - `{{TITLE}}` — text do záložky prohlížeče (téma dokumentu, bez příjemce).
   - `{{DOC_TITLE}}` — krátký titul v panelu (2–4 slova), pojmenuje téma.
   - `{{META}}` — datum (formát `dd-mm-yyyy`) · autor. **Bez „Pro <jméno>".**
   - `{{NAV}}` — `<a href="#id"><span class="n">01</span>Název</a>` pro každou sekci.
   - `{{SECTIONS}}` — sekce `<section id="id">` s `<h2>`, `<p class="lead">`, obsahem
     a technickými roletami. `id` musí sedět s kotvou v NAV a **pořadí sekcí musí sedět
     s pořadím v NAV** (přepínač je na to navázaný).
5. **Zkontroluj proti pravidlům věrnosti** — projdi hotový report a smaž vše, co ve zdroji
   není (závěry, cesty, časy).
6. **Naservíruj na localhostu** (ne file://, ne preview panel) přes sdílený skript —
   jedna složka = jeden stálý port a běžící server se znovupoužije, takže regenerace
   neplodí nové porty:
   ```bash
   ~/ai-prompts-and-skills/shared-skills/_shared/serve.sh <složka> <slug>-report.html
   ```
   Skript vypíše hotovou URL `http://127.0.0.1:<port>/<slug>-report.html` — tu pošli.
   Nikdy nespouštěj `python3 -m http.server` ručně (nechává za sebou duplicitní servery).

---

## Co je hotový výstup

- `<slug>-report.html` s vyplněným layoutem a zvoleným brand kitem.
- Běžící localhost odkaz na kontrolu.
- Zdroj pravdy zůstává raw dokument; report se z něj dá kdykoliv přestavět.

## Reference

Vzorová hotová instance layoutu: `job-springwalk/report-tomas-v2-mockup.html`
(projekt AI-brand). Pravidla vznikla tamtéž; `job-springwalk/report-skill-pravidla.md`
je jejich zrcadlo pro čtení v kontextu projektu, zdroj pravdy je tenhle soubor.
