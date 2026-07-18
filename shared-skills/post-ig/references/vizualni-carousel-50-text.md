# Vizualni carousel: 50% text + potvrzujici obraz

Pouzij pro edukativni IG carousel, kde ma text byt stejne silny jako obraz.
Cilem je performance poster: velky headline, barevne keywordy, avatar a jeden
obrazovy detail, ktery potvrzuje pointu screenu.

## Princip

Kazdy slide musi fungovat i pri rychlem scrollu:

- Text je hlavni vizual, ne popisek.
- Text zabira 50 % nebo vic, pripadne je opticky dominantni.
- Obraz text neprekrýva, ale potvrzuje.
- Avatar nedela nahodnou pozu; potvrzuje roli screenu.

## Screen plan

Pred grafikou vypln pro kazdy screen:

```markdown
Screen:
Role:
Text:
Keywordy:
Avatarova akce:
Vizualni dukaz:
Zakazana kolize:
```

Role typicky:

- hook,
- akce,
- kontrola,
- signal,
- vysledek,
- dalsi krok.

## Visual proof matrix

| Role | Co musi potvrdit obraz |
|---|---|
| Hook | Avatar ukazuje nebo se diva k problemu; text dominuje. |
| Akce | Avatar fyzicky dela akci, napr. bezi. |
| Kontrola | Stabilni line, rovnomerny rytmus, pace line, zadny chaos. |
| Signal | Dech z ust, mimika zateze, telo potvrzuje intenzitu. |
| Vysledek | Graf, prumer, threshold line, stabilni cast. |
| Dalsi krok | Posun v case, progress line, sipka, opakovani testu. |

## Image prompt bez textu

```text
Create a dark premium AI endurance coach Instagram carousel slide background.
No text, no letters, no numbers, no watermark.

Subject: recurring stylized male AI coach avatar.
Avatar action: [ACTION THAT CONFIRMS THE SCREEN].
Visual proof detail: [ONE DETAIL THAT CONFIRMS THE TEXT].
Composition: portrait 4:5, avatar on right/lower-right, left 50-60% reserved
as a clean dark navy text field. The text field must stay calm and empty.
Style: premium sports poster, AI trainer, navy background, lime and blue accents.
Avoid: text-like marks, busy left side, avatar crossing into the text field.
```

## Local text overlay

Sazet text lokalne az po vytvoreni obrazu:

- Canvas: `1080x1350`.
- Text field: idealne `x=50`, `width=650-760`, `height>=650`.
- Font: tucny sans, zadne tenke rezy.
- Hlavni text: bila.
- Primary keyword: lime.
- Secondary keyword: modra.
- Radkovani: tesne, aby text tvoril masu.
- Brand `AI TRENER` jen male nahore, pokud patri do stylu.

Technicky:

- Pokud menis jen text, negeneruj nove obrazky.
- Cesky text nacitej z UTF-8 souboru nebo pouzij Unicode escapes.
- Po renderu vzdy vytvor contact sheet.

## Final gate

Carousel je hotovy az kdyz plati:

- Text zabira 50 % nebo vic.
- Text je citelny v contact sheetu.
- Text neprekryva oblicej, telo ani dukazovy detail.
- Kazdy slide ma jasny vizualni dukaz.
- Avatarova akce sedi k textu.
- Ceska diakritika a cisla jsou spravne.
- Vsechny PNG jsou `1080x1350`.
- Ve finalni carousel slozce nejsou pomocne debug soubory.

## Failure modes

- Text je jen titulek nahore.
- Avatar dela porad stejnou pozu.
- Obraz je hezky, ale nepotvrzuje vetu.
- Text prekryva podstatnou cast obrazu.
- Image model generuje cesky text.
- Contact sheet je necitelny, i kdyz jednotlive PNG vypadaji dobre ve full size.
