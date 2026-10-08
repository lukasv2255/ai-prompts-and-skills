"""Vytiskne výkaz z localhostu do PDF přes headless Chrome.

Použití:
    python3 pdf.py <url> <výstup.pdf>

Bere URL ze serve.sh (ne file://), aby se načetly obrázky i fonty stejně jako
v prohlížeči. Headless Chrome po uložení PDF občas sám neskončí, proto skript
počká na soubor a proces ukončí. Vypíše počet stran (vyžaduje pypdf, jinak jen velikost).
"""
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def najdi_chrome():
    kandidati = {
        "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
        "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
    }.get(platform.system(), [])
    for k in kandidati + [shutil.which(n) for n in ("google-chrome", "chromium", "chrome")]:
        if k and Path(k).exists():
            return k
    sys.exit("Chrome nenalezen.")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    url, out = sys.argv[1], Path(sys.argv[2]).resolve()
    out.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as profil:
        proc = subprocess.Popen(
            [najdi_chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--user-data-dir={profil}", "--virtual-time-budget=5000",
             f"--print-to-pdf={out}", url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(120):
            if out.exists() and out.stat().st_size > 0 or proc.poll() is not None:
                break
            time.sleep(0.5)
        time.sleep(1)  # dopsání souboru
        proc.kill()
        proc.wait()
    if not out.exists():
        sys.exit("PDF nevzniklo.")
    try:
        from pypdf import PdfReader
        print(f"{out} ({len(PdfReader(out).pages)} stran)")
    except ImportError:
        print(f"{out} ({out.stat().st_size} B)")


if __name__ == "__main__":
    main()
