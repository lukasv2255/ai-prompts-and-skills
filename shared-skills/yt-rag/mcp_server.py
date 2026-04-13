"""
MCP server pro dotazování RAG knowledge base z YouTube transkriptů.
Používá numpy pro vektorové vyhledávání (bez ChromaDB).
"""

import json
import os
from pathlib import Path

import anthropic
import numpy as np
from mcp.server.fastmcp import FastMCP
from openai import OpenAI

BASE_DIR     = Path(__file__).parent
VECTORS_FILE = BASE_DIR / "vectors.npy"
META_FILE    = BASE_DIR / "metadata.json"
EMBED_MODEL  = "text-embedding-3-small"
TOP_K        = 6

mcp           = FastMCP("yt-rag")
client_oai    = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
client_claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Načti vektory a metadata do paměti při startu
vectors  = np.load(str(VECTORS_FILE)).astype(np.float32)
metadata = json.loads(META_FILE.read_text())
# Normalizuj pro cosine similarity přes dot product
norms    = np.linalg.norm(vectors, axis=1, keepdims=True)
vectors_norm = vectors / np.maximum(norms, 1e-9)


def _search(query: str, k: int = TOP_K) -> list:
    vec = client_oai.embeddings.create(model=EMBED_MODEL, input=[query]).data[0].embedding
    q   = np.array(vec, dtype=np.float32)
    q  /= max(np.linalg.norm(q), 1e-9)

    scores  = vectors_norm @ q          # cosine similarity pro všechny chunky najednou
    top_idx = np.argsort(scores)[::-1][:k]

    return [{
        "text":  metadata[i]["text"],
        "title": metadata[i]["title"],
        "url":   metadata[i]["url"],
        "score": round(float(scores[i]), 3),
    } for i in top_idx]


@mcp.tool()
def search_nick_saraev(query: str) -> str:
    """
    Prohledá transktipty YouTube kanálu Nick Saraev a vrátí nejrelevantnější úryvky.
    Použij kdykoli uživatel chce vědět co Nick Saraev říká o nějakém tématu,
    nebo se ptá na obsah jeho videí.
    """
    hits = _search(query)
    if not hits:
        return "Nic nenalezeno."

    parts = []
    for i, h in enumerate(hits, 1):
        parts.append(
            f"[{i}] {h['title']} (relevance: {h['score']})\n"
            f"URL: {h['url']}\n"
            f"{h['text'][:500]}"
        )
    return "\n\n---\n\n".join(parts)


@mcp.tool()
def ask_nick_saraev(question: str) -> str:
    """
    Odpověz na otázku nebo vytvoř shrnutí na základě obsahu YouTube kanálu Nick Saraev.
    Použij pro: shrnutí témat, vysvětlení konceptů, "co Nick říká o X", "jak funguje Y",
    nebo jakoukoliv otázku která vyžaduje syntézu z více videí.
    Vrátí strukturovanou odpověď s citacemi zdrojů.
    """
    hits = _search(question, k=8)
    if not hits:
        return "V knowledge base nebylo nic nalezeno k tomuto tématu."

    context_parts = []
    seen_titles   = set()
    budget        = 12_000

    for h in hits:
        chunk = f"[{h['title']}]\n{h['text']}\nZdroj: {h['url']}"
        if len("\n\n".join(context_parts)) + len(chunk) > budget:
            break
        context_parts.append(chunk)
        seen_titles.add(h['title'])

    context = "\n\n---\n\n".join(context_parts)
    sources = "\n".join(f"- {t}" for t in seen_titles)

    response = client_claude.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system=(
            "Jsi asistent specializovaný na obsah YouTube kanálu Nick Saraev. "
            "Odpovídej výhradně na základě poskytnutých úryvků z transkriptů. "
            "Buď konkrétní, strukturovaný a cituj z jakých videí čerpáš. "
            "Pokud téma v úryvcích není pokryto, řekni to přímo. "
            "Odpovídej v jazyce otázky."
        ),
        messages=[{
            "role": "user",
            "content": f"Úryvky z transkriptů:\n\n{context}\n\n---\n\nOtázka: {question}"
        }]
    )

    answer = response.content[0].text
    return f"{answer}\n\n---\n**Zdroje ({len(seen_titles)} videí):**\n{sources}"


@mcp.tool()
def summarize_video(title_query: str) -> str:
    """
    Shrne obsah konkrétního videa z kanálu Nick Saraev.
    Zadej část názvu videa (nemusí být přesná) — nástroj najde nejlepší shodu.
    Použij když uživatel chce shrnutí jednoho konkrétního videa.
    """
    # Najdi video podle názvu (case-insensitive substring match, fallback na nejpodobnější)
    query_lower = title_query.lower()
    matched_id  = None

    # 1. Přesná shoda podřetězce
    for item in metadata:
        if query_lower in item["title"].lower():
            matched_id = item["video_id"]
            break

    # 2. Fallback: sémantické hledání názvu
    if not matched_id:
        hits = _search(title_query, k=3)
        if hits:
            matched_id = next(
                (m["video_id"] for m in metadata if m["title"] == hits[0]["title"]),
                None
            )

    if not matched_id:
        return f"Video '{title_query}' nenalezeno. Zkus jiný název nebo část názvu."

    # Načti všechny chunky tohoto videa seřazené podle pořadí
    chunks = sorted(
        [m for m in metadata if m["video_id"] == matched_id],
        key=lambda x: x["chunk_index"]
    )
    video_title = chunks[0]["title"]
    video_url   = chunks[0]["url"]
    full_text   = " ".join(c["text"] for c in chunks)

    # Ořízni na ~14 000 znaků (přibližně 3500 tokenů kontextu)
    full_text = full_text[:14_000]

    response = client_claude.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system=(
            "Jsi asistent který shrnuje obsah YouTube videí. "
            "Vytvoř strukturované shrnutí: hlavní téma, klíčové body, praktické rady. "
            "Odpovídej v jazyce otázky."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Shrň toto video:\n"
                f"Název: {video_title}\n"
                f"URL: {video_url}\n\n"
                f"Transkript:\n{full_text}"
            )
        }]
    )

    return f"**{video_title}**\n{video_url}\n\n{response.content[0].text}"


@mcp.tool()
def list_videos(search: str = "") -> str:
    """
    Vypíše seznam videí v knowledge base.
    Volitelně filtruje podle klíčového slova v názvu.
    Použij když uživatel chce vědět jaká videa jsou dostupná.
    """
    seen = {}
    for item in metadata:
        if item["video_id"] not in seen:
            seen[item["video_id"]] = item["title"]

    titles = sorted(seen.values())

    if search:
        titles = [t for t in titles if search.lower() in t.lower()]

    if not titles:
        return f"Žádné video neobsahuje '{search}'."

    lines = [f"{i+1}. {t}" for i, t in enumerate(titles)]
    return f"Nalezeno {len(titles)} videí:\n\n" + "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
