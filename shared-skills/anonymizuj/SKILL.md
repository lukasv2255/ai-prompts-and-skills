---
name: anonymizuj
description: >
  Připraví dokument k vystavení ven — najde v něm osobní a citlivé údaje, nechá si
  potvrdit, co se zachová a co nahradí, a nahrazení provede reprodukovatelně přes
  mapu, kterou si projekt ponechá pro příští běhy. Nahrazuje smyšlenými, ale
  věrohodnými hodnotami, ne zástupkami typu XXXX. Plná verze zůstává na disku.
  Použij kdykoliv uživatel říká:
  - "anonymizuj" / "anonymizuj tenhle dokument"
  - "připrav to na web, ať tam nejsou klientská data"
  - "zanonymizuj report/nabídku/ukázku před odesláním"
  - "/anonymizuj <soubor>"
---

# anonymizuj

Dokumenty z klientských projektů obsahují cizí data. Tenhle skill z nich udělá
verzi, která smí ven, aniž by se jejich obsah rozpadl na `XXXX`.

## Tři pravidla, která platí vždy

1. **Nikdy zástupky.** Žádné `XXXX`, `[jméno]`, `***`. Číslo účtu se nahradí jiným
   číslem účtu, jméno jiným jménem, adresa jinou adresou. Dokument musí dál číst
   jako skutečný dokument — je to ukázka práce, ne formulář.
2. **Anonymizuje se identita, ne obsah.** Částky, data, formulace, právní argumenty
   a zjištění zůstávají. Kdo je smaže, zahodí zrovna to, kvůli čemu se dokument
   ukazuje.
3. **Plná verze zůstává na disku.** Anonymizuje se do kopie. Zdroj v projektu se
   nepřepisuje.

## Postup

### 1. Zjisti, co v dokumentu je

Projdi ho a **vypiš nález uživateli s počty**, po kategoriích:

- fyzické osoby — jména, rodná čísla, data narození, adresy, telefony, maily
- firmy — protistrany, věřitelé, dodavatelé, jejich IČ a sídla
- identifikátory — spisové značky, variabilní symboly, čísla smluv, čísla účtů
- částky vázané na konkrétní osobu
- snímky obrazovky z cizích systémů (ty ven nepatří vůbec, ani anonymizované)

Užitečné vzory:

```bash
grep -oE '[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' SOUBOR | sort | uniq -c
grep -oE '[0-9]{6}/[0-9]{3,4}' SOUBOR | sort | uniq -c          # rodná čísla
grep -oE '\b[0-9]{6,10}/[0-9]{4}\b' SOUBOR | sort | uniq -c     # čísla účtů
grep -oE '(\+420 ?)?[0-9]{3} ?[0-9]{3} ?[0-9]{3}' SOUBOR | sort | uniq -c
grep -oE '[A-ZŽŠČŘĎŤŇÁÉÍÓÚŮÝ][a-zžščřďťňáéíóúůýě]+, ?s\.r\.o\.|[A-Z][A-Za-z]+ a\.s\.' SOUBOR | sort | uniq -c
```

### 2. Zeptej se, co se zachová

Tohle **nikdy nerozhoduj sám**. Typicky se liší:

- firma, pro kterou se pracovalo, se často zachovat **má** — je to reference
- protistrany a jejich zákazníci se zachovat **nemají**
- vlastní zaměstnanec objednatele podepsaný pod dokumentem je hraniční případ

Zeptej se na konkrétní jména z nálezu, ne obecně. A ptej se zvlášť na fyzické
osoby, které nespadají do žádné kategorie, kterou uživatel vyjmenoval.

### 3. Napiš mapu

Mapa je JSON vedle dokumentu, typicky `<projekt>/anonymizace/mapa.json`:

```json
{
  "zachovat": ["Firma s.r.o. včetně adresy", "všechny částky"],
  "nahradit": {
    "Protistrana, s.r.o.": "Alfa Credit, s.r.o.",
    "Nováková": "Sedláčková",
    "2502651750/2010": "2701338164/2010",
    "9054023700": "9061370655"
  },
  "regex": [],
  "zakazane": ["\\b9054[0-9]{6}\\b"],
  "povolene": []
}
```

Na co myslet při psaní mapy:

- **Zkrácené tvary.** „Rerum Finance, s.r.o." se v textu dlužníka objeví i jako
  holé „Rerum". Delší klíč musí být v mapě taky, engine bere delší napřed.
- **Skloňování.** `Vlček` / `Vlčku`, `Čipera` / `Čipero`, `Dušková` / `Duškovi`.
- **Rozlišitelnost.** Každá osoba dostane vlastní náhradu, ne všichni „Novák".
  Ukázka, kde se z pěti dlužníků stane jeden, přestane dávat smysl.
- **Věrohodná čísla.** Vymyšlený účet si nech ve tvaru původního (délka, kód banky),
  ať nevypadá jako placeholder.
- `zakazane` jsou regexy, které ve výstupu **nesmí zbýt** — sem patří vzor původních
  identifikátorů. Je to pojistka proti tomu, že se na jeden výskyt zapomene.

Tvary s malými písmeny a bez diakritiky **do mapy psát nemusíš** — engine si je
dogeneruje sám. Právě na nich se to jinak láme: příjmení projde jako `Nováková`
v textu, `Novakova` v podpisu a `novakova` v mailové adrese, a kontrolní `grep`
na `Novák` ten třetí tvar nenajde.

### 4. Spusť a ověř

```bash
python3 ~/ai-prompts-and-skills/shared-skills/anonymizuj/anonymizuj.py mapa.json zdroj.html vystup.html
```

Engine dělá jeden průchod přes všechny klíče najednou, takže se nahrazený text
už znovu nemapuje. Na konci ověří výstup proti všem variantám všech klíčů i proti
`zakazane`. **Když něco zbylo, soubor nezapíše a skončí kódem 1** — doplň mapu
a spusť znovu.

Pak ještě projdi výstup očima. Engine hlídá, co je v mapě; nenajde jméno, které
tě nenapadlo. Zvlášť u textů bez diakritiky (strojové poznámky, patičky) a uvnitř
atributů HTML — `id` sekce nebo kotva v navigaci se anonymizací taky změní a musí
zůstat konzistentní s odkazy.

### 5. Napiš do dokumentu, že je anonymizovaný

Do výstupu patří viditelná poznámka — **co je nahrazené a co ne**. Bez toho čtenář
neví, jestli se dívá na skutečná čísla.

> **Anonymizovaná ukázka.** Jména dlužníků, názvy věřitelů, čísla účtů a spisové
> značky jsou nahrazené smyšlenými údaji. Částky jsou uvedené tak, jak jsou.

A zkontroluj **tvrzení, která anonymizací přestala platit**. Věta „znění jsou
doslovná" v anonymizované verzi není pravdivá a musí se upravit.

### 6. Když se zdroj změní

Pusť to znovu, ne ručně. Když projekt překlápí opakovaně (typicky na web), vyplatí
se vedle mapy držet malý skript, který zavolá engine a doplní poznámku a `noindex`
— příklad je `job-springwalk/reporty/anonymizace/na-web.py` v repu AI-brand.

## Čeho se vyvarovat

- **Nespoléhej na `grep` s velkým písmenem jako na důkaz čistoty.** To je přesně
  ta chyba, kvůli které tenhle skill vznikl.
- **Hlídej krátké klíče uvnitř jiných slov.** Engine nahrazuje jen na hranici slova,
  takže `Hrubá` už neudělá z „zhruba" nesmysl „zsimkova" — ale hranice nepomůže, když
  je klíč sám celým slovem v jiném významu (`Beta`, `Novák` jako obecné jméno, zkratka
  `AK`). Takové klíče projdi po nahrazení očima, nebo použij delší tvar.
- **Nepřepisuj zdroj.** Anonymizuje se do kopie.
- **Neanonymizuj do ztráty smyslu.** Když dokument po zásahu neukazuje, co uměl
  ukázat, je lepší ho nevystavovat vůbec než vystavit prázdný.
