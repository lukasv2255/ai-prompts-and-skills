---
name: yt-rag
description: Vytvor knowledge base z YouTube transkriptu a priprav ji pro dotazovani pres RAG. Pouzij kdyz uzivatel chce ptat se na obsah kanalu, shrnovat temata napric videi, pripravit embeddingy z transkriptu nebo vystavit YouTube archiv pro AI dotazy.
---

# YT RAG

Tento skill stavi knowledge base z YouTube kanalu: transkripty prevede na dokumenty,
naembeduje je a pripravi vrstvu pro vyhledavani a odpovidani nad obsahem videi.

Primarni use-case:

- ptat se "co rika kanal o X?"
- shrnout tema napric desitkami nebo stovkami videi
- pripravit archiv videi pro dalsi AI workflow

## Kdy ho pouzit

- uz mas transkripty a chces z nich udelat vyhledavatelnou knowledge base
- chces delat tematicka shrnuti napric celym kanalem
- potrebujes embeddingy a metadata pro dalsi aplikaci, chat nebo MCP server
- chces rychle postavit RAG vrstvu bez ChromaDB nebo tezke infrastruktury

## Závislosti

Zaklad:

```bash
pip3 install yt-dlp youtube-transcript-api openai anthropic tiktoken python-frontmatter numpy
```

Pro MCP integraci navic:

```bash
/opt/homebrew/bin/pip3 install "mcp[cli]" --break-system-packages
```

Vyžaduje:

- OpenAI API key pro embeddingy
- model nebo provider pro finalni odpovedi
- casto VPN pri hromadnem stahovani z YouTube

## Postup

### 1. Ziskej transkripty

Kdyz transkripty jeste nemas, pouzij nejdriv skill `yt-transcripts`.

Ocekavany vstup:

- `transcripts/<slug>/...`

### 2. Preved transkripty na dokumenty

Pouzij `build_rag_docs.py` z tohoto skillu. Nastav kanal:

```python
CHANNEL_NAME = "Nazev kanalu"
CHANNEL_SLUG = "slug"
CHANNEL_URL  = "https://www.youtube.com/@handle"
```

Spust:

```bash
python3 build_rag_docs.py
```

Vystup:

- `docs/<slug>/<video_id>.md`

Kazdy soubor ma metadata a cisty text transkriptu.

### 3. Naembeduj a uloz index

Pouzij `ingest.py` a nastav:

```python
DOCS_DIR = Path("docs/<slug>")
```

Spust:

```bash
source .env && python3 ingest.py
```

Vystup:

- `vectors.npy`
- `metadata.json`
- `ingest_done.json`

Tohle je jadro skillu. Od tehle chvile uz mas lokalni RAG index, ktery muzes
napojit na libovolne dotazovaci rozhrani.

### 4. Vyber rozhrani pro dotazovani

Moznosti:

- vlastni Python skript nebo web app
- agent nebo chatbot nad lokalnimi soubory
- MCP server pro Claude Code nebo Codex desktop workflow

Pro MCP variantu pouzij:

- `mcp_server.py`
- `run_mcp.sh`

To je jen jeden adapter, ne podstata celeho skillu.

## MCP / chat integrace

Pokud chces obsah vystavit jako MCP server, nastav `.env`:

```text
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Pak vytvor `.mcp.json` nebo jiny odpovidajici config pro prostredi, ktere
MCP server nacita:

```json
{
  "mcpServers": {
    "yt-rag": {
      "command": "/bin/bash",
      "args": ["/absolutni/cesta/k/run_mcp.sh"]
    }
  }
}
```

Kdyz uzivatel nepouziva MCP, tenhle krok preskoc.

## Dulezite poznamky

- `ask` nebo podobny dotazovaci endpoint typicky pracuje jen s omezenym poctem
  nejrelevantnejsich chunku. Kdyz odpoved tvrdi, ze video nebo tema "chybi",
  muze jit jen o nepresny retrieval.
- Pro ověření existence videa je lepsi mit i listovaci nebo sumarizacni nastroj.
- Tohle reseni je lehke a lokalni: `numpy` + soubory, bez tezke DB vrstvy.

## Technicke detaily

- chunking: cca 600 tokenu, 100 overlap
- embedding model: `text-embedding-3-small`
- vyhledavani: cosine similarity nad `numpy`
- generovani odpovedi: libovolny vhodny model podle prostredi

## Soubory tohoto skillu

- `SKILL.md` — workflow
- `README.md` — kratke lidske vysvetleni
- `build_rag_docs.py` — prevod transkriptu na dokumenty
- `ingest.py` — embeddingy a index
- `mcp_server.py` — volitelny MCP adapter
- `run_mcp.sh` — spousteci wrapper pro MCP adapter
