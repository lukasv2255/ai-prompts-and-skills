---
name: new-agent-project
description: Scaffold nového Python AI agenta. Použij když uživatel říká "nový projekt", "chci postavit agenta", nebo "začni nový bot/agent".
allowed-tools: Read, Write, Edit, Glob, Bash
---

# New Agent Project Scaffold

Vytvoř kompletní strukturu nového Python AI projektu.

## Co udělat

1. **Vytvoř složku projektu** v `C:\Users\tommy\claude-code\<nazev-projektu>\`

2. **Struktura:**
```
<projekt>/
  src/
    __init__.py
  prompts/
  docs/
    project_notes/
      key_facts.md
      decisions.md
      bugs.md
  tasks/
    lessons.md
  logs/         ← prázdná složka, přidej .gitkeep
  main.py
  requirements.txt
  .env.example
  .gitignore
  Procfile
  README.md
```

3. **requirements.txt** — základ:
```
python-telegram-bot==20.7
openai==1.12.0
python-dotenv==1.0.0
```
Přidej další podle potřeby projektu.

4. **.env.example:**
```
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DRY_RUN=true
```

5. **.gitignore:**
```
.env
token.json
credentials.json
logs/*.log
__pycache__/
*.pyc
.DS_Store
```

6. **Procfile:**
```
worker: python main.py
```

7. **logs/.gitkeep** — prázdný soubor aby složka existovala na Railway

8. **main.py** — základní skeleton s loggingem:
```python
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/agent.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Agent spuštěn.")


if __name__ == "__main__":
    asyncio.run(main())
```

9. **key_facts.md** — vyplň hned co víš:
```markdown
# Key Facts — <Název projektu>

## Stack
- Jazyk: Python 3.11+
- AI: OpenAI GPT-4o-mini
- Deployment: Railway + GitHub

## Infrastructure
- Railway token: [doplnit]
- Railway Project ID: [doplnit po vytvoření]
- Railway Service ID: [doplnit po vytvoření]
- GitHub repo: [doplnit]
```

## Po scaffoldu

- Inicializuj git: `git init && git add . && git commit -m "init"`
- Vytvoř GitHub repo a pushni
- Připomeň uživateli nainstalovat Railway CLI: `npm install -g @railway/cli`
