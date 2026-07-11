---
name: robust-max
description: >
  Najdi REÁLNÉ maximum (nebo práh/odhad) z hlučné řady čísel — odfiltruj nesmysly,
  ne skutečné špičky. Tři obranné vrstvy: časové okno, absolutní strop/podlaha,
  relativní konzistence vůči průvodnímu signálu.

  Použij kdykoliv zazní:
  - "reálné/skutečné maximum", "odfiltruj nesmysly", "outlier", "vadný vzorek"
  - "sanity strop", "hraniční hodnota nedává smysl", "jeden špatný záznam rozbil odhad"
  - odhad prahu / osobáku / peaku z historie (FTP, LTHR, max tep, PB, rekord)
  - "spike ze senzoru", "chyba měření nafoukla výsledek"
  - agregace kde `max()` je zranitelné vůči jediné vadné hodnotě
---

# Robustní maximum z hlučné řady

> Odzkoušeno na AI-treneru: odhad FTP ze Stravy. Naivní `max(NP)` bral kariérní
> špičku z 2016 (NP 920 W → FTP 828) i spike wattmetru → rozbité IF/TSS/CTL.
> Tři vrstvy filtru srazily odhad na reálných ~230 W bez ztráty dobrých dat.

## Kdy to řešit

Vždy, když bereš `max()` (nebo `min`) přes naměřená/importovaná čísla a **jediná
vadná hodnota zkreslí výsledek**. Typicky: odhad prahu z historie, osobní rekord,
peak výkonu, nejvyšší cena, maximální latence. `max` je z definice nejcitlivější
na outliery — chytne přesně tu jednu chybu, kterou nechceš.

**Klíčový rozdíl oproti „vyhoď outliery statisticky":** nechceš useknout skutečné
špičky (percentil/IQR to udělá). Chceš zahodit jen **nesmysly** — hodnoty, které
jsou fyzikálně/doménově nemožné nebo nekonzistentní. Skutečný rekord musí projít.

---

## Tři obranné vrstvy

Skládej je podle povahy dat. Každá chytá jinou třídu chyb.

### ① Časové okno — když číslo reprezentuje AKTUÁLNÍ stav, ne historii

Hledáš-li současnou kondici/výkon (ne kariérní rekord), ber jen z relevantního okna
relativně k nejnovějšímu vzorku. Odřízne roky staré — a často korumpované — špičky.

```python
from datetime import date, timedelta

def within_window(records, days, date_of):
    """Ponech jen záznamy z posledních `days` dní vůči NEJNOVĚJŠÍMU záznamu
    (ne vůči dnešku — data můžou končit v minulosti). date_of(r) -> 'YYYY-MM-DD'."""
    dates = [d for d in (date_of(r) for r in records) if d]
    if not dates:
        return records
    cutoff = (date.fromisoformat(max(dates)) - timedelta(days=days)).isoformat()
    return [r for r in records if (date_of(r) or "") >= cutoff]
```

Kdy **ne**: když opravdu chceš all-time rekord (PB, absolutní maximum). Pak okno vynech.

### ② Absolutní strop / podlaha — doménová sanity

Zahoď hodnoty mimo fyzikálně/doménově reálný rozsah. Konstanta pojmenovaná a
okomentovaná — je to doménové rozhodnutí, ne magické číslo.

```python
def robust_max(values, cap=None, floor=None):
    """Maximum po odfiltrování None a hodnot mimo [floor, cap].
    None když po filtru nic nezbude (volající pak jede na fallback)."""
    kept = [v for v in values
            if v is not None
            and (floor is None or v >= floor)
            and (cap is None or v <= cap)]
    return max(kept) if kept else None
```

**Pozor na umístění stropu.** Dvě různá chování:
- **Strop na jednotlivé hodnoty** (výše) → vadný vzorek zmizí, výsledek se dopočítá
  z dobrých dat. *Chirurgické — preferuj.*
- **Strop na finální výsledek** (`est if est <= CAP else None`) → jediná vysoká
  hodnota zahodí CELÝ odhad na None. *Tupé — jen jako poslední pojistka.*

### ③ Relativní konzistence — cross-check vůči průvodnímu signálu

Nejsilnější vrstva: outlier, který projde oknem i stropem, ale je nekonzistentní
vůči druhé veličině. U FTP: normalizovaný výkon (NP) je z definice ≥ průměr; poměr
NP/avg (variability index) je reálně ~1,0–1,4. Poměr 2,75 (NP 550 / avg 200) =
Strava odhad výkonu bez wattmetru → zahoď, i když je NP pod stropem.

```python
def consistent(record, primary, companion, max_ratio):
    """True, když primary/companion nepřekračuje max_ratio. Chybí-li companion,
    kontrolu NEPROVÁDÍME (neházet pryč legitimní vzorek kvůli chybějícímu poli)."""
    p, c = record.get(primary), record.get(companion)
    return not c or (p is not None and p <= c * max_ratio)
```

Kdy **ne**: nemáš-li druhý korelovaný signál. Nevymýšlej ho uměle.

---

## Složený příklad (vzor z FTP)

Vrstvy se skládají jako postupné filtry. Pořadí: okno → konzistence → strop na hodnotu.

```python
_WINDOW_DAYS = 365     # aktuální forma, ne kariéra
_MAX_VI      = 1.5     # poměr NP/avg nad 1,5 = fyzikální nesmysl
_CAP         = 600     # W — fyziologický strop odhadu

def estimate_peak(records):
    recent = within_window(records, _WINDOW_DAYS, lambda r: r.get("date"))
    candidates = [r["np"] for r in recent
                  if r.get("np") and consistent(r, "np", "avg", _MAX_VI)]
    return robust_max(candidates, cap=_CAP)   # None → fallback (jiná metoda)
```

---

## Rozhodovací pravidla (naučeno v praxi)

- **`max`, ne percentil, když na hodnotě visí kalibrace.** U FTP se maximum násobí
  ověřeným faktorem (0,90). p95 by tiše podstřelil vstup → rozladil kalibraci.
  Percentil ber jen tam, kde outlierů je hodně a žádná konstanta na max nenavazuje
  (např. `max tep = p95` kvůli spikům hrudního pásu — tam je šum systematický).
- **Filtruj vadný vzorek, ne celý výsledek.** Chirurgický filtr (① ② na hodnoty, ③)
  zachová dobrá data; tupý strop na výsledek zahodí všechno kvůli jedné chybě.
- **Fallback při None.** Když po filtru nic nezbude, vrať None a měj náhradní cestu
  (u FTP: sport jede na hrTSS, než trenér doplní ruční hodnotu). Nikdy nehádej.
- **Konstanty pojmenuj a okomentuj PROČ.** Strop/okno/poměr jsou doménová rozhodnutí.
- **Chybějící companion ≠ vadný vzorek.** ③ přeskoč, když druhý signál chybí.

## Pasti

- **Okno vůči dnešku místo vůči datům.** Data můžou končit v minulosti → počítej
  cutoff z `max(dates)`, ne z `date.today()`.
- **Strop moc těsně.** Nastav ho na doménový extrém (nejlepší reálný sportovec),
  ne na běžnou hodnotu — jinak useknout skutečné špičky.
- **`max([])` spadne.** Vždy ošetři prázdno po filtru (`return None`).
- **Tichá ztráta všech dat.** Když každý vzorek propadne filtrem, výsledek je None —
  loguj/hlídej to, ať nezmizí odhad bez povšimnutí.

## Test checklist

- happy path: reálné maximum projde nezměněné
- jeden vadný vzorek (nad stropem / nereálný poměr / mimo okno) → ignorován, odhad z dobrých
- všechny vzorky vadné → None + fallback
- prázdný vstup → None (ne pád)
- companion chybí → ③ se přeskočí, vzorek se počítá
