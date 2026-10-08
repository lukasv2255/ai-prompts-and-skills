"""Koláčové grafy „% hotovo“ k blokům výkazu.

Použití:
    python3 grafy.py <grafy.json> [--barva "#de492a"] [--out <složka>]

grafy.json je seznam bloků:
    [{"soubor": "blok-1.png", "nadpis": "Název bloku", "hotovo": 80}]
Graf je bez legendy a všechny mají stejnou velikost plátna. --barva je primární barva
značky (--primary z ../report-na-web/brands/<slug>.css). --out default = složka JSONu.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEDA = "#e5e7ec"
TEXT = "#181a20"
TLUMENY = "#7a7c85"


def graf(cil, nadpis, hotovo, barva):
    fig, ax = plt.subplots(figsize=(5.6, 6.0), dpi=120)
    hodnoty = [hotovo] + ([100 - hotovo] if hotovo < 100 else [])
    ax.pie(hodnoty, colors=[barva, SEDA][: len(hodnoty)], startangle=90, counterclock=False,
           wedgeprops={"width": 0.36, "edgecolor": "white", "linewidth": 2})
    ax.text(0, 0.08, f"{hotovo} %", ha="center", va="center", fontsize=40, fontweight="bold", color=TEXT)
    ax.text(0, -0.2, "hotovo", ha="center", va="center", fontsize=15, color=TLUMENY)
    ax.set_title(nadpis, fontsize=19, fontweight="bold", color=TEXT, pad=14)
    # pevné plátno bez ořezu, aby měly všechny grafy stejnou velikost
    fig.subplots_adjust(left=0.04, right=0.96, bottom=0.03, top=0.88)

    fig.savefig(cil, facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--barva", default="#1A4D2E")
    ap.add_argument("--out")
    a = ap.parse_args()
    data = Path(a.data).resolve()
    out = Path(a.out).resolve() if a.out else data.parent
    for b in json.loads(data.read_text(encoding="utf-8")):
        graf(out / b["soubor"], b["nadpis"], int(b["hotovo"]), a.barva)
        print(out / b["soubor"])


if __name__ == "__main__":
    main()
