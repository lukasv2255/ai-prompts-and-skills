#!/usr/bin/env python3
"""Naservíruje HTML soubor nebo složku tak, aby to šlo otevřít na telefonu.

Výchozí režim je LAN — server poslouchá na všech rozhraních a odkaz obsahuje
adresu počítače v místní síti. Telefon na stejné Wi-Fi ho otevře, ven z bytu
se nic nedostane.

S přepínačem --tunnel se navíc pustí cloudflared quick tunnel a vznikne
veřejná https adresa, která funguje odkudkoli a bez přihlašování — za cenu
toho, že obsah je po dobu běhu dostupný komukoli, kdo adresu zná.

Skript sám najde volný port (nikdy nekilluje cizí proces), po startu ověří,
že na portu je opravdu jeho vlastní obsah, a vypíše výsledek jako JSON.
Pak drží běh, dokud ho někdo neukončí.

    python3 serve_tunnel.py <cesta> [--tunnel] [--port-from 9200]
"""
import argparse
import http.server
import json
import re
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.request import urlopen

STATE = Path(tempfile.gettempdir()) / "odkaz-na-mobil.json"


def lan_ip():
    """Adresa počítače v místní síti. Bez odesílání dat — jen se zeptáme jádra."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.168.1.1", 1))  # nikam se nepřipojuje, jen vybere rozhraní
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


def spust_server(koren: Path, port_od: int, bind: str):
    """Zabere první skutečně volný port. Obsazený port se přeskočí, nikdy nekilluje."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(koren), **kw)

        def log_message(self, *a):
            pass

    for port in range(port_od, port_od + 60):
        try:
            srv = socketserver.TCPServer((bind, port), Handler)
        except OSError:
            continue  # port drží někdo jiný — jdeme na další
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        return srv, port
    sys.exit("Nenašel jsem volný port.")


def title(url: str, pokusy: int = 8) -> str:
    """Titulek stránky — důkaz, že odpovídá náš server a ne cizí.

    Čerstvá trycloudflare doména chvíli není v DNS, proto se to opakuje;
    bez toho by kontrola spadla na adrese, která za pár vteřin funguje.
    """
    chyba = "?"
    for pokus in range(pokusy):
        try:
            html = urlopen(url, timeout=10).read(4000).decode("utf-8", "replace")
        except Exception as e:
            chyba = str(e)
            time.sleep(6)
            continue
        m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
        return m.group(1).strip() if m else "(bez titulku)"
    return f"CHYBA: {chyba}"


def spust_tunel(port: int) -> str:
    log = Path(tempfile.gettempdir()) / "odkaz-na-mobil-tunnel.log"
    with open(log, "w") as f:
        subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"],
            stdout=f, stderr=subprocess.STDOUT,
        )
    for _ in range(40):
        time.sleep(1)
        m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", log.read_text())
        if m:
            return m.group(0)
    sys.exit(f"Tunel nenaběhl. Log: {log}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cesta", help="HTML soubor nebo složka")
    ap.add_argument("--tunnel", action="store_true", help="veřejná adresa přes cloudflared")
    ap.add_argument("--port-from", type=int, default=9200)
    args = ap.parse_args()

    cil = Path(args.cesta).expanduser().resolve()
    if not cil.exists():
        sys.exit(f"Neexistuje: {cil}")
    koren = cil if cil.is_dir() else cil.parent
    vychozi = "" if cil.is_dir() else cil.name

    # tunel čte z localhostu, LAN potřebuje všechna rozhraní
    srv, port = spust_server(koren, args.port_from, "127.0.0.1" if args.tunnel else "0.0.0.0")

    if args.tunnel:
        zaklad = spust_tunel(port)
        # cloudflared ohlásí adresu dřív, než ji zná DNS. Bez téhle pauzy
        # spadne první dotaz a macOS si tu neúspěšnou odpověď zacachuje.
        time.sleep(10)
    else:
        ip = lan_ip()
        if not ip:
            sys.exit("Nenašel jsem adresu v místní síti — zkus --tunnel.")
        zaklad = f"http://{ip}:{port}"

    # ověření: každá stránka musí odpovědět naším titulkem
    stranky = sorted(p.name for p in koren.glob("*.html"))
    kontrola = {s: title(f"{zaklad}/{s}") for s in stranky}

    vysledek = {
        "url": f"{zaklad}/{vychozi}" if vychozi else zaklad,
        "rezim": "tunel (veřejné)" if args.tunnel else "LAN (jen místní síť)",
        "port": port,
        "koren": str(koren),
        "stranky": kontrola,
    }
    STATE.write_text(json.dumps(vysledek, ensure_ascii=False, indent=2))
    print(json.dumps(vysledek, ensure_ascii=False, indent=2), flush=True)

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
