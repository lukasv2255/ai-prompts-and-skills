# Key Facts — Klíčové konfigurace

> Claude: nehavluj konfigurace ani technologie — hledej zde.

---

## Stack

- **Jazyk:** Python 3.11+
- **AI APIs:** OpenAI (GPT-4, embeddings), Anthropic (Claude)
- **Vector DB:** ChromaDB
- **Deployment:** Railway (server), GitHub (verzování)
- **Boti:** python-telegram-bot
- **Frontend:** HTML/JS (jednoduché, bez frameworku)

## API klíče (vždy v .env, nikdy v kódu)

```
OPENAI_API_KEY=        # OpenAI GPT + embeddings
ANTHROPIC_API_KEY=     # Claude API
TELEGRAM_BOT_TOKEN=    # Telegram bot
```

## Nasazené projekty

| Projekt | URL | Platform |
|---|---|---|
| RAG citační vyhledávač | [doplnit Railway URL] | Railway |
| Rohlik bot | Telegram | Telegram |

## ChromaDB

- Lokální persistent storage: `./chroma_db/`
- Embedding model: `text-embedding-ada-002` (OpenAI) nebo `text-embedding-3-small`
- Collection: `[doplnit název kolekce]`
- Počet dokumentů: ~1000 studií

## Railway deployment

- Push na GitHub main → automatický deploy
- Env proměnné nastaveny přímo v Railway dashboardu (ne v .env souboru)
- `Procfile` nebo `railway.json` pro definici start příkazu

## Rohlik.cz bot

- Komunikace přes Telegram
- [Doplnit: jak funguje přihlášení na Rohlik]
- [Doplnit: co přesně bot umí — přidání do košíku? objednání?]
