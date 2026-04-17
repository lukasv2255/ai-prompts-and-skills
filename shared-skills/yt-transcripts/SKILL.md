---
name: yt-transcripts
description: >
  Hromadné stahování transkriptů z YouTube kanálů s automatickým watchdogem.
  yt-dlp + Chrome cookies, rate-limit skip logika, watchdog pro automatický restart.

  Použij kdykoliv uživatel říká:
  - "stáhni transkripty z YouTube" / "stahni transkripty [kanál]"
  - "přidej YouTube kanál ke stahování"
  - "spusť stahování" / "nastartuj stahování"
  - "zastav stahování" / "stop watchdog"
  - "stav" (pokud probíhá nebo probíhalo stahování transkriptů)
  - "jak to jde se stahováním"
  - jakýkoliv dotaz na průběh stahování transkriptů

---

# YT Transcripts — hromadné stahování transkriptů

Stahuje titulky ze všech videí zadaných YouTube kanálů. Ukládá jako `.txt` soubory,
sleduje progress, přeskakuje kanály při rate limitu a vrací se k nim na konci.
Watchdog automaticky restartuje skript po rate limitu — bez zásahu uživatele.

---

## ⚠️ Před spuštěním

1. **VPN zapnutá** — YouTube blokuje hromadné stahování. Bez VPN = rate limit po desítkách videí.
2. **Chrome přihlášen na YouTube** — yt-dlp čte cookies z Chrome.
3. Závislosti: `pip3 install yt-dlp youtube-transcript-api`

---

## Přidání kanálu

Uprav `CHANNELS` v `download_transcripts.py`:

```python
CHANNELS = [
    {"name": "Název kanálu", "url": "https://www.youtube.com/@handle", "slug": "slug_pro_slozku"},
]
```

---

## Spuštění (vždy spusť obojí dohromady)

```bash
# 1. Watchdog — hlídá a restartuje download při rate limitu
bash watchdog.sh &

# 2. Download — pokud watchdog ještě nespustil
pgrep -f download_transcripts.py || python3 download_transcripts.py >> download.log 2>&1 &
```

Watchdog každých 5 minut kontroluje jestli `download_transcripts.py` běží — pokud ne, restartuje ho.
Díky tomu stahování pokračuje automaticky i po rate limitu bez zásahu uživatele.

---

## Zastavení

```bash
# Zastav watchdog i download
pkill -f watchdog.sh; pkill -f download_transcripts.py
echo "Zastaveno."
```

---

## Stav stahování

Při dotazu na stav spusť:

```bash
pgrep -f watchdog.sh && echo "watchdog: bezi" || echo "watchdog: nespi"
pgrep -f download_transcripts.py && echo "download: bezi" || echo "download: nespi"
cat transcript_progress.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for k, v in d.items():
    total = len(v['done']) + len(v['failed'])
    print(f'{k}: {len(v[\"done\"])} done, {len(v[\"failed\"])} failed')
"
tail -2 download.log
```

Formát odpovědi:

| Kanál | Staženo | Selhalo |
|---|---|---|
| název | X | Y |
| **Celkem** | **N** | |

Watchdog: běží / neběží — + jedna věta co se aktuálně děje.

---

## Přeskočení zaseknutého videa

Pokud se stahování opakovaně zasekává na stejném videu:

```bash
# Zjisti ID videa ze seznamu kanálu
python3 -m yt_dlp --flat-playlist --print "%(id)s\t%(title)s" --no-warnings \
  --cookies-from-browser chrome "https://www.youtube.com/@KANAL/videos" | grep -i "HLEDANY_NAZEV"

# Přidej ID do failed v progress.json
python3 -c "
import json
p = json.load(open('transcript_progress.json'))
p['SLUG']['failed'].append('VIDEO_ID')
json.dump(p, open('transcript_progress.json', 'w'), indent=2)
print('Přidáno do failed')
"
```

Pak restart watchdog + download (viz Spuštění výše).

---

## Rate limit logika

- Po **5 rate limitech za sebou** → přeskočí kanál, pokračuje dalším
- Po dokončení ostatních → vrátí se k přeskočeným (5min pauza)
- Mezi videi: **1.5–3s**, každých 50 videí pauza **8–15s**

---

## Struktura souborů

```
projekt/
├── download_transcripts.py   # hlavní skript — uprav CHANNELS
├── watchdog.sh               # daemon — restartuje download po rate limitu
├── transcript_progress.json  # průběh (automaticky)
├── download.log              # log stahování
├── watchdog.log              # log watchdogu
└── transcripts/
    └── kanal_slug/
        └── VIDEO_ID.txt      # Title + Video ID + plain text přepis
```
