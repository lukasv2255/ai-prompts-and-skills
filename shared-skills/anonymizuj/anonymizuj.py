#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""anonymizuj — nahradi citlive udaje v dokumentu podle mapy a overi, ze nic neuniklo.

Proc vlastni engine a ne rada `sed` prikazu: pri rucnim mapovani se spolehlive
zapomene na tvary teze polozky. Prijmeni "Riesova" projde jako "Riesová" v textu,
"Riesova" v podpisu a "riesova" v mailove adrese — a kontrolni grep na "Riesov"
ten treti tvar nenajde. Engine proto ke kazde dvojici sam dogeneruje varianty
(male/velke pismena, bez diakritiky) a na konci overi vystup proti vsem z nich.

Pouziti:
    python3 anonymizuj.py mapa.json zdroj.html vystup.html

Mapa je JSON:
{
  "nahradit":  {"Puvodni": "Nahrada", ...},   # doslovne retezce, delsi maji prednost
  "regex":     [["vzor", "nahrada"], ...],    # az po "nahradit", pro cisla a vzory
  "zachovat":  ["Fieldcollect", ...],         # co se vedome NEanonymizuje (jen dokumentace)
  "zakazane":  ["vzor"],                      # regexy, ktere ve vystupu nesmi zbyt
  "povolene":  ["vzor"]                       # vyjimky ze "zakazane"
}

Navratovy kod 1 = ve vystupu neco zbylo, soubor se nezapsal.
"""
import json, re, sys, unicodedata
from pathlib import Path


def bez_diakritiky(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def varianty(puvodni: str, nahrada: str):
    """Ke dvojici dogeneruje tvary, na ktere se pri rucnim psani mapy zapomina."""
    dvojice = {(puvodni, nahrada)}
    for tvar in (str.lower, str.upper, bez_diakritiky):
        dvojice.add((tvar(puvodni), tvar(nahrada)))
        # bez diakritiky A zaroven malymi — typicky mailova adresa
        dvojice.add((bez_diakritiky(tvar(puvodni)).lower(),
                     bez_diakritiky(tvar(nahrada)).lower()))
    return {(p, n) for p, n in dvojice if p}


def na_hranici(klic: str) -> str:
    """Obali klic hranici slova, aby se netrefil doprostred jineho slova.

    Bez toho udela zaznam "Hruba" -> "Simkova" ze slova "zhruba" nesmysl
    "zsimkova". Hranice se pridava jen na tu stranu, kde klic zacina nebo
    konci pismenem ci cislici — u klice "CentroFinance, s.r.o." by jinak
    tecka na konci hranici nikdy nesplnila.
    """
    vzor = re.escape(klic)
    if klic[:1].isalnum():
        vzor = r"(?<!\w)" + vzor
    if klic[-1:].isalnum():
        vzor = vzor + r"(?!\w)"
    return vzor


def nahrad(text: str, mapa: dict) -> str:
    """Jeden pruchod pres vsechny klice naraz — nahrazeny text uz se znovu nemapuje."""
    tabulka = {}
    for puvodni, nahrada in mapa.get("nahradit", {}).items():
        for p, n in varianty(puvodni, nahrada):
            tabulka.setdefault(p, n)
    if tabulka:
        klice = sorted(tabulka, key=len, reverse=True)   # delsi tvar vyhrava
        vzor = re.compile("|".join(na_hranici(k) for k in klice))
        text = vzor.sub(lambda m: tabulka[m.group(0)], text)
    for vzor, nahrada in mapa.get("regex", []):
        text = re.sub(vzor, nahrada, text)
    return text


def zkontroluj(text: str, mapa: dict):
    """Vraci seznam toho, co ve vystupu zbylo. Prazdny seznam = cisto."""
    zbylo = []
    for puvodni, nahrada in mapa.get("nahradit", {}).items():
        for p, _ in varianty(puvodni, nahrada):
            # tataz hranice jako pri nahrazovani, jinak by "zhruba" hlasilo "hruba"
            if p and re.search(na_hranici(p), text):
                zbylo.append(p)
    povolene = [re.compile(v) for v in mapa.get("povolene", [])]
    for vzor in mapa.get("zakazane", []):
        for nalez in re.findall(vzor, text):
            kus = nalez if isinstance(nalez, str) else nalez[0]
            if not any(v.fullmatch(kus) for v in povolene):
                zbylo.append(kus)
    return sorted(set(zbylo))


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    mapa = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    text = nahrad(Path(sys.argv[2]).read_text(encoding="utf-8"), mapa)

    zbylo = zkontroluj(text, mapa)
    if zbylo:
        print("ANONYMIZACE NEUPLNA — ve vystupu zbylo:", file=sys.stderr)
        for z in zbylo:
            print("   ", z, file=sys.stderr)
        print("\nSoubor se nezapsal. Doplnit do mapy a spustit znovu.", file=sys.stderr)
        sys.exit(1)

    Path(sys.argv[3]).write_text(text, encoding="utf-8")
    print(f"zapsano: {sys.argv[3]} ({len(text)} znaku)")
    if mapa.get("zachovat"):
        print("vedome zachovano:", ", ".join(mapa["zachovat"]))
    print("kontrola: cisto")


if __name__ == "__main__":
    main()
