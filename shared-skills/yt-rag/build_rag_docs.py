"""
Převede stažené transktipty na .md soubory vhodné pro RAG.

Výstup: docs/nicksaraev/<video_id>.md

Každý soubor má YAML frontmatter s metadaty + čistý text transkriptu.
"""

import re
from pathlib import Path

CHANNEL_NAME  = "Nick Saraev"
CHANNEL_SLUG  = "nicksaraev"
CHANNEL_URL   = "https://www.youtube.com/@nicksaraev"

INPUT_DIR  = Path("transcripts") / CHANNEL_SLUG
OUTPUT_DIR = Path("docs") / CHANNEL_SLUG


def parse_transcript(txt_path: Path):
    text = txt_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = video_id = None
    content_start = 0

    for i, line in enumerate(lines):
        if line.startswith("Title: "):
            title = line[len("Title: "):].strip()
        elif line.startswith("Video ID: "):
            video_id = line[len("Video ID: "):].strip()
        elif title and video_id and line.strip() == "":
            content_start = i + 1
            break

    if not title or not video_id:
        return None

    content = " ".join(lines[content_start:]).strip()
    content = re.sub(r" +", " ", content)

    return {"title": title, "video_id": video_id, "content": content}


def to_markdown(doc: dict) -> str:
    # Escapování uvozovek v titulku pro YAML
    safe_title = doc["title"].replace('"', '\\"')
    url = f"https://www.youtube.com/watch?v={doc['video_id']}"

    return f"""---
title: "{safe_title}"
video_id: "{doc['video_id']}"
channel: "{CHANNEL_NAME}"
channel_url: "{CHANNEL_URL}"
url: "{url}"
---

# {doc['title']}

{doc['content']}
"""


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(INPUT_DIR.glob("*.txt"))
    ok = skipped = 0

    for txt_path in txt_files:
        doc = parse_transcript(txt_path)
        if not doc:
            print(f"  ✗ skip: {txt_path.name}")
            skipped += 1
            continue

        out_path = OUTPUT_DIR / f"{doc['video_id']}.md"
        out_path.write_text(to_markdown(doc), encoding="utf-8")
        ok += 1

    print(f"\nHotovo: {ok} .md souborů → {OUTPUT_DIR}/")
    if skipped:
        print(f"Přeskočeno (chybí metadata): {skipped}")


if __name__ == "__main__":
    main()
