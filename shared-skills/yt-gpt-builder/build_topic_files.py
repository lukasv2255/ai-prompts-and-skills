"""
build_topic_files.py

1. Pro každý transkript zavolá GPT-4o-mini a přiřadí 1-2 témata
2. Sloučí transkripty do 15 tematických souborů pro OpenAI Assistant

Výstup: topic_files/<téma>.txt
Progress: topic_classification.json (bezpečné přerušení a pokračování)

Cena: ~$1-2 za 5000 transkriptů
"""

import json
import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TOPICS = [
    "protein_a_svalova_hmota",
    "hubnutí_a_metabolismus",
    "strevni_mikrobiom",
    "kardiovaskularni_zdravi",
    "dlouhovekost_a_starnuti",
    "spanek_a_regenerace",
    "vyziva_a_diety",
    "cviceni_a_vykon",
    "mozek_a_mentalni_zdravi",
    "hormony_a_metabolismus",
    "zanet_a_imunita",
    "vitaminy_a_suplementy",
    "prevence_rakoviny",
    "zeny_a_zdravi",
    "ultra_prumyslove_potraviny",
]

TOPIC_LABELS = {
    "protein_a_svalova_hmota": "Protein & svalová hmota",
    "hubnutí_a_metabolismus": "Hubnutí & metabolismus",
    "strevni_mikrobiom": "Střevní mikrobiom",
    "kardiovaskularni_zdravi": "Kardiovaskulární zdraví",
    "dlouhovekost_a_starnuti": "Dlouhověkost & stárnutí",
    "spanek_a_regenerace": "Spánek & regenerace",
    "vyziva_a_diety": "Výživa & diety",
    "cviceni_a_vykon": "Cvičení & výkon",
    "mozek_a_mentalni_zdravi": "Mozek & mentální zdraví",
    "hormony_a_metabolismus": "Hormony & metabolismus",
    "zanet_a_imunita": "Zánět & imunita",
    "vitaminy_a_suplementy": "Vitamíny & suplementy",
    "prevence_rakoviny": "Prevence rakoviny",
    "zeny_a_zdravi": "Ženy & zdraví",
    "ultra_prumyslove_potraviny": "Ultra-průmyslové potraviny",
}

TRANSCRIPTS_DIR = Path("transcripts")
OUTPUT_DIR = Path("topic_files")
PROGRESS_FILE = Path("topic_classification.json")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = f"""Jsi klasifikátor vědeckých podcastů o zdraví a výživě.
Dostaneš přepis podcastu. Vrať 1-2 témata ze seznamu, která nejlépe vystihují hlavní obsah.

Dostupná témata:
{chr(10).join(f"- {t}" for t in TOPICS)}

Odpověz POUZE jako JSON pole s tématy. Příklad:
["protein_a_svalova_hmota", "cviceni_a_vykon"]

Pokud podcast nepasuje do žádného tématu, vrať prázdné pole: []
"""


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}


def save_progress(progress: dict):
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


def classify_transcript(title: str, text: str) -> list[str]:
    # Posíláme jen prvních ~800 slov — stačí pro klasifikaci
    words = text.split()[:800]
    preview = " ".join(words)

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Název: {title}\n\nObsah: {preview}"},
                ],
                max_tokens=50,
                temperature=0,
            )
            raw = response.choices[0].message.content.strip()
            if not raw:
                time.sleep(2)
                continue
            topics = json.loads(raw)
            return [t for t in topics if t in TOPICS]
        except json.JSONDecodeError:
            time.sleep(2)
        except Exception as e:
            print(f"    Chyba: {e}")
            time.sleep(5)
    return []


def collect_all_transcripts() -> list[dict]:
    transcripts = []
    for txt_file in sorted(TRANSCRIPTS_DIR.glob("*/*.txt")):
        content = txt_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = lines[0].replace("Title: ", "").strip() if lines else txt_file.stem
        video_id = lines[1].replace("Video ID: ", "").strip() if len(lines) > 1 else txt_file.stem
        text = "\n".join(lines[3:]) if len(lines) > 3 else content
        channel_slug = txt_file.parent.name
        transcripts.append({
            "file": str(txt_file),
            "title": title,
            "video_id": video_id,
            "channel": channel_slug,
            "text": text,
        })
    return transcripts


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    transcripts = collect_all_transcripts()
    print(f"Nalezeno {len(transcripts)} transkriptů\n")

    progress = load_progress()
    classified = 0
    skipped = 0

    for i, t in enumerate(transcripts):
        key = t["video_id"]

        if key in progress:
            skipped += 1
            continue

        print(f"[{i+1}/{len(transcripts)}] {t['title'][:60]}...", end=" ", flush=True)
        topics = classify_transcript(t["title"], t["text"])
        progress[key] = {"topics": topics, "title": t["title"], "channel": t["channel"]}

        if topics:
            print(f"→ {', '.join(topics)}")
        else:
            print("→ (žádné téma)")

        classified += 1

        if classified % 20 == 0:
            save_progress(progress)

        time.sleep(0.1)  # rate limit buffer

    save_progress(progress)
    print(f"\nKlasifikace hotova: {classified} nových, {skipped} přeskočeno\n")

    # ── Merge do tematických souborů ────────────────────────────────────────
    print("Vytvářím tematické soubory...")

    # Připrav slovník text per téma
    topic_content: dict[str, list[str]] = {t: [] for t in TOPICS}

    transcript_map = {t["video_id"]: t for t in transcripts}

    for video_id, meta in progress.items():
        if video_id not in transcript_map:
            continue
        t = transcript_map[video_id]
        entry = f"## {t['title']}\nZdroj: {t['channel']} | ID: {video_id}\n\n{t['text']}\n\n---\n"
        for topic in meta["topics"]:
            if topic in topic_content:
                topic_content[topic].append(entry)

    for topic, entries in topic_content.items():
        if not entries:
            print(f"  ⚠ {TOPIC_LABELS[topic]}: žádné transkripty")
            continue

        out_path = OUTPUT_DIR / f"{topic}.txt"
        header = f"# {TOPIC_LABELS[topic]}\nPočet videí: {len(entries)}\n\n"
        out_path.write_text(header + "\n".join(entries), encoding="utf-8")
        size_mb = out_path.stat().st_size / 1024 / 1024
        print(f"  ✓ {TOPIC_LABELS[topic]}: {len(entries)} videí ({size_mb:.1f} MB)")

    print(f"\nHotovo → složka: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
