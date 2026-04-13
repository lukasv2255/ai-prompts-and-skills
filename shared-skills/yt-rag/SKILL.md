# YT RAG — Knowledge Base z YouTube kanálu

Stáhne transktipty YouTube kanálu, embeduje je a zpřístupní jako MCP nástroj
v Claude Code. Primární use-case: **ptát se na obsah videí a získávat shrnutí témat**.

---

## Kdy použít

- Chceš se ptát "co říká [kanál] o X?"
- Chceš shrnutí tématu napříč stovkami videí
- Chceš mít obsah kanálu dostupný přímo v Claude chatu

---

## Závislosti

```bash
pip3 install yt-dlp youtube-transcript-api openai anthropic tiktoken python-frontmatter numpy
/opt/homebrew/bin/pip3 install "mcp[cli]" --break-system-packages  # Python 3.14 pro MCP
```

**Vyžaduje:**
- OpenAI API klíč (embeddingy — ~$0.002 na celý ingest)
- Anthropic API klíč (generování odpovědí — ~$0.001 na dotaz)
- VPN při stahování transkriptů (YouTube blokuje hromadné stahování)

---

## Postup

### 1. Stáhni transktipty

Použij skill `yt-transcripts`. Nastaví kanál, spustí stahování, uloží do `transcripts/<slug>/`.

### 2. Převeď na .md soubory

Zkopíruj `build_rag_docs.py` z tohoto skillu do projektu. Nastav kanál:

```python
CHANNEL_NAME = "Název kanálu"
CHANNEL_SLUG = "slug"
CHANNEL_URL  = "https://www.youtube.com/@handle"
```

Spusť:
```bash
python3 build_rag_docs.py
```

Výstup: `docs/<slug>/<video_id>.md` — každý soubor má YAML frontmatter (title, video_id, url) a čistý text transkriptu.

### 3. Embeduj a ulož vektory

Zkopíruj `ingest.py` z tohoto skillu. Nastav:

```python
DOCS_DIR = Path("docs/<slug>")
```

Spusť:
```bash
source .env && python3 ingest.py
```

Výstup:
- `vectors.npy` — matice embeddingů (N × 1536)
- `metadata.json` — texty a metadata chunků
- `ingest_done.json` — progress (bezpečné přerušení a pokračování)

**Pozn.:** Při rate limitu (429) skript automaticky čeká a zkouší znovu.

### 4. MCP server

Zkopíruj `mcp_server.py` a `run_mcp.sh` z tohoto skillu. Nastav `.env`:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Vytvoř `.mcp.json` v kořeni projektu:
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

Otevři projekt v Claude Code desktop — server se načte automaticky.

---

## Dostupné nástroje v Claude chatu

| Nástroj | Použití |
|---|---|
| `search_<slug>` | Rychlé vyhledání nejrelevantnějších úryvků (surové chunky) |
| `ask_<slug>` | Odpověď na otázku ze všech videí najednou (sémantické hledání) |
| `summarize_video` | Shrnutí **konkrétního videa** — zadej část názvu |
| `list_videos` | Výpis dostupných videí, volitelně filtrovaný |

### Jak správně dotazovat

**Otázka napříč kanálem** → `ask_nick_saraev`
- *"Co říká Nick o cold emailech?"*
- *"Jak vydělávat s n8n?"*
- *"Jaký je rozdíl mezi n8n a Claude Code?"*

**Shrnutí konkrétního videa** → `summarize_video`
- *"Shrň video CLAUDE SKILLS FULL COURSE"*
- *"Sumarizuj video o cold email kurzu"*
- *"Co je v kurzu o n8n?"*

**Nevíš jak se video jmenuje?** → `list_videos`
- *"Jaká videa mám v databázi?"*
- *"Vypiš videa která mají 'skills' v názvu"*

### Důležité upozornění

`ask` vrací jen **8 nejrelevantnějších chunků** — pokud říká "video chybí", neverit mu.
Databáze může mít video, ale dotaz nebyl dost přesný. Vždy použij `summarize_video`
nebo `list_videos` pro ověření.

---

## Technické detaily

- **Chunking:** 600 tokenů, 100 overlap — vhodné pro plynulý řečový text bez odstavců
- **Embedding model:** `text-embedding-3-small` (1536 dimenzí, $0.02/1M tokenů)
- **Vyhledávání:** cosine similarity přes numpy (bez ChromaDB — segfaultuje na macOS)
- **Generování:** Claude Haiku (~$0.001/dotaz)

---

## Soubory tohoto skillu

- `SKILL.md` — tento průvodce
- `build_rag_docs.py` — převod transkriptů na .md
- `ingest.py` — embedování a ukládání vektorů
- `mcp_server.py` — MCP server se čtyřmi nástroji
- `run_mcp.sh` — wrapper pro spuštění MCP serveru

ARGUMENTS: <channel_url>
