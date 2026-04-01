---
name: telegram-bot-setup
description: Nastav nového Telegram bota — BotFather, token, Chat ID. Použij když uživatel říká "nový telegram bot", "potřebuji telegram bota", nebo "nastav telegram".
allowed-tools: Read, Write, Edit, Bash, WebFetch
---

# Telegram Bot Setup

## Krok 1 — Vytvoř bota přes BotFather

Řekni uživateli:
1. Otevři Telegram a napiš **@BotFather**
2. Pošli příkaz `/newbot`
3. Zadej název bota (zobrazovaný, např. "Mail Agent")
4. Zadej username bota (musí končit na `bot`, např. `mail_agent_bot`)
5. BotFather odpoví tokenem — zkopíruj celý řetězec

Token vypadá takto: `1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Krok 2 — Získej Chat ID

Řekni uživateli:
1. Napiš svému novému botovi **libovolnou zprávu** (např. "ahoj")
2. Otevři v prohlížeči tuto URL (nahraď TOKEN):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. V JSON odpovědi najdi `"chat":{"id": XXXXXXX}` — to je Chat ID

Pokud `"result":[]` (prázdné) → uživatel ještě nepsal botovi. Připomeň mu to.

## Krok 3 — Ulož do .env

```
TELEGRAM_BOT_TOKEN=<token od BotFather>
TELEGRAM_CHAT_ID=<číslo z getUpdates>
```

## Krok 4 — Ulož do key_facts.md

Přidej do `docs/project_notes/key_facts.md`:
```markdown
## Telegram
- Bot token: (v .env jako TELEGRAM_BOT_TOKEN)
- Chat ID: <číslo>
```

## Krok 5 — Otestuj

Spusť v terminálu (nahraď hodnoty):
```bash
python -c "
import asyncio
from telegram import Bot
async def test():
    bot = Bot('<TOKEN>')
    await bot.send_message(chat_id=<CHAT_ID>, text='Bot funguje!')
asyncio.run(test())
"
```

Pokud přišla zpráva do Telegramu — hotovo.

## Časté problémy

| Problém | Příčina | Fix |
|---------|---------|-----|
| `getUpdates` vrací `[]` | Uživatel nepsal botovi | Napiš botovi zprávu, pak obnov URL |
| `Unauthorized` | Špatný token | Zkopíruj token znovu z BotFather |
| Bot neodpovídá | Jiný bot má stejný webhook | Každý projekt musí mít vlastního bota |
