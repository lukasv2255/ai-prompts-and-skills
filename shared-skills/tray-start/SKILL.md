---
name: tray-start
description: Spustí shopping agent (Rohlik.cz Telegram bot) jako tray aplikaci na pozadí ve Windows. Použij kdykoliv uživatel říká "spusť bota", "spusť tray", "nastartuj shopping agenta", "spusť rohlik bota", nebo chce bot spustit na pozadí.
---

# Spuštění Shopping Agent tray aplikace

Spusť příkaz v adresáři projektu:

```bash
cd C:/Users/tommy/claude-code/shopping-agent && pythonw tray.py
```

Po spuštění:
- Zkontroluj, že proces běží: `tasklist | grep pythonw`
- Oznam uživateli: "Bot spuštěn — ikonka je v system tray. Pro ukončení klikni na ikonku → Ukončit."

Pokud `pythonw` není dostupný, zkus `python tray.py` (otevře se konzolové okno).
