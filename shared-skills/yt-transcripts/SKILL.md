---
name: yt-transcripts
description: >
  Hromadné stahování transkriptů z YouTube kanálů.
  yt-dlp + Chrome cookies, rate-limit skip logika, watchdog pro automatický restart,
  LaunchAgent pro běh přes noc.

  Použij kdykoliv uživatel říká:
  - "stáhni transkripty z YouTube"
  - "chci texty ze všech videí kanálu"
  - "přidej YouTube kanál ke stahování"
  - "jak to jde se stahováním"
  - "stav" (pokud právě běží stahování transkriptů)
  - jakýkoliv dotaz na aktuální stav stahování

## Stav stahování — jak reportovat

Pokud uživatel napíše "stav" nebo se ptá na průběh stahování, spusť tyto příkazy
a vrať přehledný report:

```bash
pgrep -f download_transcripts.py && echo "bezi" || echo "nespi"
cat transcript_progress.json | python3 -c "import json,sys; d=json.load(sys.stdin); [print(k, 'done:', len(v['done']), 'failed:', len(v['failed'])) for k,v in d.items()]"
ls transcripts/*/*.txt 2>/dev/null | wc -l
tail -2 download.log
```

Formát odpovědi:

📊 **Stav**

| Kanál | Staženo | Selhalo |
|---|---|---|
| Název kanálu | X / celkem | Y |
| **Celkem na disku** | **N** | |

+ jedna věta co se aktuálně děje (běží/zaseknutý/hotovo).
---

# YT Transcripts — hromadné stahování transkriptů

Stahuje titulky ze všech videí zadaných YouTube kanálů. Ukládá jako `.txt` soubory,
sleduje progress, přeskakuje kanály při rate limitu a vrací se k nim na konci.

---

## ⚠️ Před spuštěním

**Nutné podmínky:**
1. **VPN zapnutá** — YouTube agresivně blokuje hromadné stahování. Bez VPN = rate limit po desítkách videí.
2. **Chrome přihlášen na YouTube** — yt-dlp čte cookies z Chrome pro autorizaci.
3. Nainstalované závislosti: `pip3 install yt-dlp youtube-transcript-api`

---

## Struktura souborů

```
projekt/
├── download_transcripts.py   # hlavní skript
├── watchdog.sh               # hlídá a restartuje skript
├── transcript_progress.json  # průběh (automaticky)
├── download.log              # log stahování
├── watchdog.log              # log watchdogu
└── transcripts/
    ├── kanal_1/
    │   ├── VIDEO_ID.txt
    │   └── ...
    └── kanal_2/
        └── ...
```

Každý `.txt` soubor obsahuje:
```
Title: Název videa
Video ID: abc123

[celý přepis jako plain text]
```

---

## Jak spustit

### 1. Nastav kanály v `download_transcripts.py`

```python
CHANNELS = [
    {"name": "Název kanálu", "url": "https://www.youtube.com/@handle", "slug": "slug_pro_slozku"},
    # ...
]
```

### 2. Spusť stahování

```bash
python3 download_transcripts.py >> download.log 2>&1 &
```

### 3. Nastav watchdog (běh přes noc)

```bash
# Zkopíruj watchdog.sh do projektu a uprav DIR= cestu
bash watchdog.sh &

# Nebo jako LaunchAgent (přežije restart Macu):
cp cz.lukas.transcript-watchdog.plist ~/Library/LaunchAgents/
# Uprav cestu v plistu
launchctl load ~/Library/LaunchAgents/cz.lukas.transcript-watchdog.plist
```

### 4. Nastav cron hlídač (Claude session)

Spusť CronCreate každých 5 minut:
```
Zkontroluj jestli běží download_transcripts.py v /cesta/k/projektu — pokud ne, spusť ho znovu na pozadí. Jinak nedělej nic.
```

### 5. Sleduj průběh

```bash
tail -f download.log
```

---

## Rate limit logika

- Po **5 rate limitech za sebou** → přeskočí kanál, pokračuje dalším
- Po dokončení všech ostatních → vrátí se k přeskočeným s 5min pauzou
- Mezi videi čeká **1.5–3s**, každých 50 videí pauza **8–15s**

---

## Přidání nových kanálů

Přidej do seznamu `CHANNELS`, skript automaticky přeskočí již stažená videa (progress tracking).

---

## Soubory tohoto skillu

- `download_transcripts.py` — generický skript (uprav CHANNELS)
- `watchdog.sh` — watchdog daemon
- `launchagent.plist` — macOS LaunchAgent šablona
