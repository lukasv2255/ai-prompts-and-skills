# YT Transcripts

Hromadné stahování transkriptů ze YouTube kanálů jako `.txt` soubory.

## ⚠️ Před spuštěním

| Požadavek | Proč |
|---|---|
| **VPN zapnutá** | YouTube blokuje hromadné stahování po desítkách videí |
| **Chrome přihlášen na YouTube** | yt-dlp čte cookies pro autorizaci |
| `pip3 install yt-dlp` | stahování a extrakce titulků |

---

## Rychlý start

```bash
# 1. Zkopíruj skripty do projektu
cp download_transcripts.py watchdog.sh /muj-projekt/

# 2. Nastav kanály v download_transcripts.py
CHANNELS = [
    {"name": "Název", "url": "https://www.youtube.com/@handle", "slug": "slozka"},
]

# 3. Spusť (s VPN!)
bash watchdog.sh &
```

---

## Výstup

```
transcripts/
├── slozka_kanalu/
│   ├── VIDEO_ID.txt    ← Title + Video ID + plain text přepisu
│   └── ...
transcript_progress.json  ← průběh (pro resume po přerušení)
download.log              ← log stahování
watchdog.log              ← log watchdogu
```

---

## Rate limit logika

Pokud YouTube vrátí 429 (Too Many Requests):
- Čeká **60–90s** a zkouší znovu
- Po **5 pokusech za sebou** → přeskočí kanál
- Po dokončení ostatních kanálů → zkusí přeskočené znovu (s 5min pauzou)

---

## Watchdog

`watchdog.sh` každých 5 minut zkontroluje jestli skript běží. Pokud ne — restartuje.

Pro automatický start po restartu Macu:
```bash
# Uprav cestu v launchagent.plist, pak:
cp launchagent.plist ~/Library/LaunchAgents/cz.lukas.transcript-watchdog.plist
launchctl load ~/Library/LaunchAgents/cz.lukas.transcript-watchdog.plist
```

---

## Resume po přerušení

Skript automaticky přeskočí již stažená videa — stačí ho znovu spustit.

---

## Soubory

| Soubor | Popis |
|---|---|
| `download_transcripts.py` | hlavní skript — nastav CHANNELS |
| `watchdog.sh` | hlídá a restartuje skript |
| `launchagent.plist` | macOS LaunchAgent šablona |
