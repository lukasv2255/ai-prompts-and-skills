---
name: prezentace
description: >
  Postaví jednostránkovou HTML prezentaci (nabídka, návrh, pitch) laděnou do značky
  příjemce. Vejde se na jeden viewport bez scrollování, text je krátký a bez
  vysvětlování. Servíruje na localhostu.

  Použij kdykoliv uživatel říká:
  - "udělej z toho webovou prezentaci"
  - "prezentace ve stylu jejich webu"
  - "nabídka / návrh pro firmu X jako HTML"
  - "/prezentace"
---

# prezentace — jednostránkový návrh laděný do značky

Cíl: jeden ekran, který příjemce přečte za 30 sekund a pochopí, co mu nabízím.
Není to dokument ani deck s 12 slajdy. Je to **plakát s argumentem**.

---

## Tvrdá pravidla (nikdy se neptej, prostě dodrž)

1. **Jedna stránka, jeden viewport, žádné scrollování.**
   `html,body{height:100%;overflow:hidden}` + `body{display:grid;grid-template-rows:...}`.
   Pod 900 px šířky se to překlopí do jednoho sloupce se scrollem (mobil jinak nejde).
2. **Max 3–4 obsahové bloky.** Víc se na obrazovku nevejde čitelně.
3. **Max 2 věty na blok.** Když to potřebuje třetí větu, patří to do přílohy, ne sem.
4. **Typografie na `clamp(min, calc(Xvh + Yvw), max)`** — musí sednout na ultrawide
   3840×1600 i na 16:9 notebook. Nikdy pevné `px` u nadpisů.
5. **Barvy a font vytáhni z webu příjemce**, ne z hlavy:
   ```bash
   curl -sL <url> | grep -oE '#[0-9a-fA-F]{6}' | sort | uniq -c | sort -rn | head
   curl -sL <url> | grep -oE 'font-family:[^;"}]+' | head
   ```
   Když je web JS-renderovaný (Wix, Webflow), vytáhni tokeny přes Playwright
   `getComputedStyle` nad viditelnými elementy.
6. **Servíruj na localhostu** (`python3 -m http.server <port>`, port mimo 8080–8089),
   pošli klikací odkaz. Nikdy `file://`, nikdy preview panel.
7. **Print styl** pro export do PDF přes Cmd+P: `@page{size:landscape}` +
   `print-color-adjust:exact` na barevné plochy.

## Struktura, která funguje

```
[tmavý pruh]   nadpis (co nabízím) + jedna věta co to je
[3 sloupce]    proč / jak / co — každý 3–4 řádky, oddělené linkou, žádné karty
[tmavý pruh]   jeden konkrétní nález nebo důkaz + odkaz na detail + rozsah/cena
```

Detail (celá analýza, čísla, zdroje) jde do **samostatného scrollovatelného dokumentu**,
na který se z prezentace odkazuje. Prezentace ho nikdy nepolyká.

## Textová pravidla

- Žádné vysvětlování, jak něco funguje, když to není to, co se prodává.
- Žádné „nejde o X, ale o Y", žádné pravidelné trojice, žádné superlativy.
- Jedna poctivá výhrada někde v textu (kde to nefunguje / co neřeším) —
  udělá to zbytek uvěřitelným.
- Konkrétní jména, čísla a data. Číslo bez data je šum.
- Čeština, věty krátké. Když jde věta přeříznout na dvě, přeřízni ji.

## Anti-slop check před odesláním

- Nekonečná mřížka stejných karet s ikonkou → ne.
- Gradienty, barevná čárka u každého boxu, `box-shadow` všude → ne.
- Zaměnitelný SaaS look bez vztahu ke značce příjemce → ne.
- Emoji v nadpisech → ne.

## Výstup

- `prezentace.html` — jednostránkový návrh.
- (volitelně) `<téma>.html` — scrollovatelný detail/analýza, stejné brand tokeny.
- Běžící server + klikací odkaz v odpovědi.
