---
name: tray-app
description: >
  Systémový tray (menu bar) pro dlouhodobě běžící Python skripty na macOS.
  Start/stop z ikony v menu baru, logování do souboru, správný Python (Homebrew).

  Použij PROAKTIVNĚ kdykoliv projekt potřebuje:
  - "spusť na pozadí", "běží pořád", "collector na pozadí"
  - "tray ikona", "menu bar", "systémová lišta"
  - "spusť přes tray", "tray.py"
  - dlouhodobě běžící Python skript na macOS
  - ovládání skriptu bez terminálu
---

# Tray App — macOS menu bar pro Python skripty

Odzkoušeno na spread-monitor: collector běží na pozadí, ovládá se z menu baru.

---

## DŮLEŽITÉ: Homebrew Python

`pystray` vyžaduje přístup k macOS GUI — **systémový Python (`/usr/bin/python3`) to neumí**.
Vždy používej Homebrew Python:

```bash
# Správná cesta
/opt/homebrew/bin/python3 tray.py

# Ověření že pystray funguje
/opt/homebrew/bin/python3 -c "import pystray; print('OK')"

# Instalace pokud chybí
/opt/homebrew/bin/pip3 install pystray pillow
```

**Proč Homebrew Python:** macOS systémový Python je izolovaný a nemá přístup k GUI frameworkům (AppKit). Homebrew Python (`/opt/homebrew/bin/python3`) má plný přístup.

---

## Základní `tray.py`

```python
"""
tray.py — Systémový tray pro správu collectoru.
Spouštěj vždy přes: /opt/homebrew/bin/python3 tray.py
"""
import subprocess, threading, signal, os, sys
from pathlib import Path
import pystray
from PIL import Image, ImageDraw

# --- Konfigurace ---
SCRIPT      = Path(__file__).parent / "collector.py"   # co spouštět
PYTHON      = sys.executable                            # stejný Python jako tray
LOG_FILE    = Path(__file__).parent / "collector_log.txt"
ICON_SIZE   = 64

# --- Stav ---
process: subprocess.Popen = None

# --- Ikona ---
def make_icon(color: str) -> Image.Image:
    """Vytvoří jednoduchou kulatou ikonu. Zelená = běží, šedá = zastaveno."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, ICON_SIZE - 8, ICON_SIZE - 8], fill=color)
    return img

# --- Akce ---
def start_collector(icon, item):
    global process
    if process and process.poll() is None:
        return  # Už běží

    log = open(LOG_FILE, "a")
    process = subprocess.Popen(
        [PYTHON, str(SCRIPT)],
        stdout=log, stderr=log,
        cwd=str(SCRIPT.parent)
    )
    icon.icon  = make_icon("#00cc44")   # zelená
    icon.title = "Collector: BĚŽÍ"

def stop_collector(icon, item):
    global process
    if process and process.poll() is None:
        process.terminate()
        process.wait(timeout=5)
    icon.icon  = make_icon("#888888")   # šedá
    icon.title = "Collector: ZASTAVEN"

def quit_app(icon, item):
    stop_collector(icon, item)
    icon.stop()

def open_log(icon, item):
    subprocess.Popen(["open", str(LOG_FILE)])

# --- Menu ---
def build_menu():
    return pystray.Menu(
        pystray.MenuItem("▶ Spustit",   start_collector),
        pystray.MenuItem("■ Zastavit",  stop_collector),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("📄 Zobrazit log", open_log),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("✕ Ukončit",   quit_app),
    )

# --- Spuštění ---
if __name__ == "__main__":
    icon = pystray.Icon(
        name="collector",
        icon=make_icon("#888888"),
        title="Collector: ZASTAVEN",
        menu=build_menu()
    )
    # Automaticky spusť collector při otevření tray
    threading.Thread(target=start_collector, args=(icon, None), daemon=True).start()
    icon.run()
```

---

## Spuštění

```bash
# Vždy Homebrew Python
/opt/homebrew/bin/python3 tray.py
```

**Správné chování:**
- Ikona se objeví v menu baru (vpravo nahoře)
- Zelená = collector běží, šedá = zastaven
- Po kliknutí se zobrazí menu

---

## Logování v collectoru

Collector loguje do `collector_log.txt` v kořeni projektu. Tray ho otevírá přes `open` (macOS Preview / TextEdit).

```python
# V collector.py — přidej na začátek
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),          # stdout (pro tray log)
        # FileHandler není nutný — tray přesměrovává stdout do souboru
    ]
)

logger = logging.getLogger(__name__)

# Pak místo print():
logger.info("Collector spuštěn")
logger.error(f"Chyba: {e}")
```

---

## Instalace závislostí

```bash
# Jednou, Homebrew Python
/opt/homebrew/bin/pip3 install pystray pillow
```

`pillow` — pro tvorbu ikony (Image, ImageDraw)
`pystray` — systémový tray

---

## Časté problémy

| Problém | Příčina | Fix |
|---------|---------|-----|
| `ModuleNotFoundError: pystray` | Použit systémový Python | Spusť přes `/opt/homebrew/bin/python3 tray.py` |
| Ikona se neobjeví | Python nemá přístup k GUI | Musí být Homebrew Python, ne systémový |
| Collector se nespustí | Špatná cesta k `collector.py` | Zkontroluj `SCRIPT = Path(__file__).parent / "collector.py"` |
| `pgrep -f collector.py` nic nenajde | Collector se nepustil nebo hned crashnul | Zkontroluj `collector_log.txt` |
| Tray se nezobrazí na Ventura+ | macOS accessibility permissions | System Settings → Privacy → Accessibility → přidej Python |

---

## Ovládání z terminálu (alternativa)

Pokud nepotřebuješ GUI, stačí:

```bash
# Spusť na pozadí, loguj do souboru
nohup /opt/homebrew/bin/python3 collector.py >> collector_log.txt 2>&1 &
echo $! > collector.pid

# Zastav
kill $(cat collector.pid)

# Sleduj log
tail -f collector_log.txt
```
