"""
Hromadné stahování YouTube transkriptů.

⚠️  Vyžaduje VPN — bez ní YouTube blokuje po desítkách videí.
⚠️  Vyžaduje Chrome přihlášený na YouTube (yt-dlp čte cookies).

Nastav CHANNELS níže a spusť:
    python3 download_transcripts.py >> download.log 2>&1 &

Soubory se ukládají do transcripts/<slug>/<video_id>.txt
Progress se ukládá do transcript_progress.json
"""

import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

# ── Konfigurace kanálů ─────────────────────────────────────────────────────
CHANNELS = [
    # {"name": "Název kanálu", "url": "https://www.youtube.com/@handle", "slug": "slug"},
]

# ── Cesty ──────────────────────────────────────────────────────────────────
TRANSCRIPTS_DIR = Path("transcripts")
PROGRESS_FILE   = Path("transcript_progress.json")
TMP_DIR         = Path("/tmp/yt_transcripts")

# ── Rychlost stahování ─────────────────────────────────────────────────────
DELAY_MIN       = 1.5   # sekund mezi videi (min)
DELAY_MAX       = 3.0   # sekund mezi videi (max)
PAUSE_EVERY     = 50    # extra pauza každých N videí
PAUSE_DURATION  = (8, 15)
RATE_LIMIT_WAIT = (60, 90)   # čekání při 429 (sekund)
RATE_LIMIT_MAX  = 5          # po kolika 429 za sebou přeskočit kanál


# ── Helpers ────────────────────────────────────────────────────────────────

def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}


def save_progress(progress: dict):
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


def get_channel_video_ids(channel_url: str) -> list[dict]:
    print("  Fetching video list...")
    result = subprocess.run(
        [
            sys.executable, "-m", "yt_dlp",
            "--flat-playlist",
            "--print", "%(id)s\t%(title)s",
            "--no-warnings",
            "--cookies-from-browser", "chrome",
            f"{channel_url}/videos",
        ],
        capture_output=True,
        text=True,
    )
    videos = []
    for line in result.stdout.strip().splitlines():
        if "\t" in line:
            vid_id, title = line.split("\t", 1)
            videos.append({"id": vid_id, "title": title})
    return videos


def json3_to_text(json3_path: Path) -> str:
    data = json.loads(json3_path.read_text(encoding="utf-8"))
    parts = []
    for event in data.get("events", []):
        for seg in event.get("segs", []):
            parts.append(seg.get("utf8", ""))
    text = " ".join(parts)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def download_transcript(video_id: str, title: str, out_path: Path) -> str:
    """Vrátí: 'ok' | 'no_transcript' | 'rate_limit'"""
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    tmp_base = TMP_DIR / video_id

    for f in TMP_DIR.glob(f"{video_id}*"):
        f.unlink()

    result = subprocess.run(
        [
            sys.executable, "-m", "yt_dlp",
            "--write-auto-sub",
            "--write-sub",
            "--sub-lang", "en",
            "--skip-download",
            "--sub-format", "json3",
            "--no-warnings",
            "--cookies-from-browser", "chrome",
            "-o", str(tmp_base),
            f"https://www.youtube.com/watch?v={video_id}",
        ],
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    if "429" in output or "Too Many Requests" in output:
        return "rate_limit"

    json3_files = list(TMP_DIR.glob(f"{video_id}*.json3"))
    if not json3_files:
        return "no_transcript"

    try:
        text = json3_to_text(json3_files[0])
        if not text.strip():
            return "no_transcript"
        out_path.write_text(f"Title: {title}\nVideo ID: {video_id}\n\n{text}", encoding="utf-8")
        for f in TMP_DIR.glob(f"{video_id}*"):
            f.unlink()
        return "ok"
    except Exception as e:
        print(f"\n    Parse error: {e}")
        return "no_transcript"


# ── Hlavní smyčka ──────────────────────────────────────────────────────────

def process_channel(channel: dict, progress: dict) -> tuple[list, bool]:
    """Zpracuje jeden kanál. Vrátí (skipped_channel_or_empty, skip_flag)."""
    slug = channel["slug"]
    name = channel["name"]
    print(f"\n{'='*60}")
    print(f"Channel: {name}")
    print(f"{'='*60}")

    out_dir = TRANSCRIPTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    if slug not in progress:
        progress[slug] = {"done": [], "failed": []}

    done_ids   = set(progress[slug]["done"])
    failed_ids = set(progress[slug]["failed"])

    videos = get_channel_video_ids(channel["url"])
    print(f"  Found {len(videos)} videos")

    downloaded = failed = skipped = 0
    consecutive_rl = 0
    skip_channel = False
    i = 0

    while i < len(videos) and not skip_channel:
        vid_id = videos[i]["id"]
        title  = videos[i]["title"]
        out_path = out_dir / f"{vid_id}.txt"

        if vid_id in done_ids or out_path.exists() or vid_id in failed_ids:
            skipped += 1
            i += 1
            continue

        print(f"  [{i+1}/{len(videos)}] {title[:60]}...", end=" ", flush=True)
        result = download_transcript(vid_id, title, out_path)

        if result == "ok":
            print("✓")
            progress[slug]["done"].append(vid_id)
            done_ids.add(vid_id)
            downloaded += 1
            consecutive_rl = 0
            i += 1
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        elif result == "no_transcript":
            print("✗ (no transcript)")
            progress[slug]["failed"].append(vid_id)
            failed_ids.add(vid_id)
            failed += 1
            consecutive_rl = 0
            i += 1
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        elif result == "rate_limit":
            consecutive_rl += 1
            if consecutive_rl >= RATE_LIMIT_MAX:
                print(f"⚠ {RATE_LIMIT_MAX}x rate limit — přeskakuji kanál, vrátím se později")
                save_progress(progress)
                skip_channel = True
            else:
                wait = random.uniform(*RATE_LIMIT_WAIT)
                print(f"⚠ rate limit ({consecutive_rl}/{RATE_LIMIT_MAX}) — čekám {wait:.0f}s")
                save_progress(progress)
                time.sleep(wait)

        processed = downloaded + failed
        if processed > 0 and processed % 10 == 0:
            save_progress(progress)
        if processed > 0 and processed % PAUSE_EVERY == 0:
            pause = random.uniform(*PAUSE_DURATION)
            print(f"  [pauza {pause:.0f}s]")
            time.sleep(pause)

    save_progress(progress)

    if skip_channel:
        print(f"  Přeskočeno (rate limit) — bude zopakováno na konci")
    else:
        print(f"  Done: {len(progress[slug]['done'])} | Failed: {len(progress[slug]['failed'])}")

    return skip_channel


def main():
    print("⚠️  Ujisti se že máš zapnutou VPN — YouTube blokuje hromadné stahování!\n")

    if not CHANNELS:
        print("❌ Žádné kanály nejsou nastaveny. Uprav CHANNELS v tomto souboru.")
        return

    progress = load_progress()
    skipped_channels = []

    for channel in CHANNELS:
        skipped = process_channel(channel, progress)
        if skipped:
            skipped_channels.append(channel)

    # Zkus přeskočené kanály znovu (po pauze)
    if skipped_channels:
        print(f"\n{'='*60}")
        print(f"Opakuji {len(skipped_channels)} přeskočených kanálů (čekám 5 minut)...")
        time.sleep(300)

        for channel in skipped_channels:
            process_channel(channel, progress)

    # Závěrečný souhrn
    progress = load_progress()
    total = sum(len(v["done"]) for v in progress.values())
    total_failed = sum(len(v["failed"]) for v in progress.values())
    print(f"\n{'='*60}")
    print(f"HOTOVO — celkem staženo: {total} | bez transkriptu: {total_failed}")
    for slug, v in progress.items():
        print(f"  {slug}: {len(v['done'])} done, {len(v['failed'])} failed")


if __name__ == "__main__":
    main()
