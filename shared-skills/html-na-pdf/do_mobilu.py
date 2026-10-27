"""Pošle soubor (typicky hotové PDF) přes iMessage na Lukášův mobil (sdílený skill html-na-pdf).

Použití:
    python3 do_mobilu.py <soubor> [text zprávy]

Jen macOS (řídí aplikaci Zprávy přes osascript). Příjemce (telefonní číslo nebo
Apple ID) je v env proměnné IMESSAGE_TO, jinak v ~/.config/do-mobilu/prijemce —
mimo git, aby číslo neleželo v repu.

Zprávy z AppleScriptu neodešlou soubor mimo svůj sandbox, proto se kopíruje
do ~/Pictures/do-mobilu/ a posílá se odtud. Soubor musí jít jako `alias`:
holý `POSIX file` Zprávy bez chyby zahodí a dorazí jen text (ověřeno 20-10-2026).
"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

KONFIG = Path.home() / ".config" / "do-mobilu" / "prijemce"
SCHRANKA = Path.home() / "Pictures" / "do-mobilu"

SKRIPT = '''
on run {prijemce, cesta, zprava}
    tell application "Messages"
        set ucet to 1st account whose service type = iMessage
        set kdo to participant prijemce of ucet
        if zprava is not "" then send zprava to kdo
        send ((POSIX file cesta) as alias) to kdo
    end tell
end run
'''


def prijemce():
    kdo = os.environ.get("IMESSAGE_TO") or (KONFIG.read_text().strip() if KONFIG.exists() else "")
    if not kdo:
        sys.exit(f"Chybí příjemce: nastav IMESSAGE_TO nebo zapiš číslo do {KONFIG}")
    return kdo


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    if platform.system() != "Darwin":
        sys.exit("iMessage jde jen na Macu.")
    soubor = Path(sys.argv[1]).resolve()
    if not soubor.exists():
        sys.exit(f"Soubor neexistuje: {soubor}")
    zprava = sys.argv[2] if len(sys.argv) == 3 else ""
    SCHRANKA.mkdir(parents=True, exist_ok=True)
    kopie = SCHRANKA / soubor.name
    shutil.copy2(soubor, kopie)
    vysledek = subprocess.run(["osascript", "-e", SKRIPT, prijemce(), str(kopie), zprava],
                              capture_output=True, text=True)
    if vysledek.returncode:
        sys.exit(f"Odeslání selhalo: {vysledek.stderr.strip()}")
    print(f"Odesláno přes iMessage: {soubor.name}")


if __name__ == "__main__":
    main()
