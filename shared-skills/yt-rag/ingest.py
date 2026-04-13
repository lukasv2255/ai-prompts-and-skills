"""
Načte .md soubory z docs/, rozřeže na chunky, embeduje a uloží jako numpy soubory.

Spuštění:
    python3 ingest.py

Výstup:
    vectors.npy     — matice embeddingů (N x 1536)
    metadata.json   — seznam {title, video_id, url, text} pro každý chunk
    ingest_done.json — seznam hotových video_id (pro pokračování po přerušení)
"""

import json
import os
import re
import time
from pathlib import Path

import frontmatter
import numpy as np
import tiktoken
from openai import OpenAI

# ── Konfigurace ────────────────────────────────────────────────────────────
DOCS_DIR      = Path("docs/nicksaraev")
VECTORS_FILE  = Path("vectors.npy")
META_FILE     = Path("metadata.json")
PROGRESS_FILE = Path("ingest_done.json")
EMBED_MODEL   = "text-embedding-3-small"
CHUNK_SIZE    = 600
CHUNK_OVERLAP = 100

client_oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tokenizer  = tiktoken.get_encoding("cl100k_base")


# ── Progress ───────────────────────────────────────────────────────────────

def load_state():
    done = set(json.loads(PROGRESS_FILE.read_text())) if PROGRESS_FILE.exists() else set()
    vectors = np.load(str(VECTORS_FILE)).tolist() if VECTORS_FILE.exists() else []
    metadata = json.loads(META_FILE.read_text()) if META_FILE.exists() else []
    return done, vectors, metadata

def save_state(done, vectors, metadata):
    PROGRESS_FILE.write_text(json.dumps(sorted(done)))
    np.save(str(VECTORS_FILE), np.array(vectors, dtype=np.float32))
    META_FILE.write_text(json.dumps(metadata, ensure_ascii=False))


# ── Chunking ───────────────────────────────────────────────────────────────

def chunk_text(text: str) -> list:
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunks.append(tokenizer.decode(tokens[start:end]))
        if end >= len(tokens):
            break
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def embed(texts: list) -> list:
    for attempt in range(5):
        try:
            response = client_oai.embeddings.create(model=EMBED_MODEL, input=texts)
            time.sleep(0.3)
            return [item.embedding for item in response.data]
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                wait = 2 ** attempt
                print(f"\n  ⚠ rate limit, čekám {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Embed selhal po 5 pokusech")


# ── Ingest ─────────────────────────────────────────────────────────────────

def main():
    md_files = sorted(DOCS_DIR.glob("*.md"))
    print(f"Nalezeno {len(md_files)} souborů\n")

    done, vectors, metadata = load_state()
    print(f"Již hotovo: {len(done)} videí, {len(vectors)} chunků\n")

    new_done = skipped = 0

    for md_path in md_files:
        post     = frontmatter.load(md_path)
        title    = post.get("title", md_path.stem)
        video_id = post.get("video_id", md_path.stem)
        url      = post.get("url", "")

        if video_id in done:
            skipped += 1
            continue

        content = re.sub(r"^#.+\n", "", post.content, count=1).strip()
        if not content:
            continue

        chunks = chunk_text(content)
        if not chunks:
            continue

        chunk_vectors = embed(chunks)

        for i, (chunk, vec) in enumerate(zip(chunks, chunk_vectors)):
            vectors.append(vec)
            metadata.append({
                "title":    title,
                "video_id": video_id,
                "url":      url,
                "text":     chunk,
                "chunk_index": i,
            })

        done.add(video_id)
        save_state(done, vectors, metadata)
        print(f"  ✓ {title[:55]} — {len(chunks)} chunks")
        new_done += 1

    print(f"\nHotovo: +{new_done} videí, {skipped} přeskočeno")
    print(f"Celkem: {len(done)} videí, {len(vectors)} chunků")
    print(f"Uloženo: {VECTORS_FILE} ({Path(str(VECTORS_FILE)).stat().st_size // 1024} KB), {META_FILE}")


if __name__ == "__main__":
    main()
