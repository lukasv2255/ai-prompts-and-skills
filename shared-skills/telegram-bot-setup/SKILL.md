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

| Problém                 | Příčina                    | Fix                                   |
| ----------------------- | -------------------------- | ------------------------------------- |
| `getUpdates` vrací `[]` | Uživatel nepsal botovi     | Napiš botovi zprávu, pak obnov URL    |
| `Unauthorized`          | Špatný token               | Zkopíruj token znovu z BotFather      |
| Bot neodpovídá          | Jiný bot má stejný webhook | Každý projekt musí mít vlastního bota |

---

## Zkušenosti z Mail Agenta — obecné principy

### 409 Conflict — dva boti se stejným tokenem

**Symptom:** `telegram.error.Conflict: terminated by other getUpdates request`

Každý token smí mít jen jednu aktivní polling instanci. Pokud běží agent na více místech (Railway + lokálně, Mac + Windows), vzniká 409.

**Řešení: jeden bot = jedno prostředí**

| Prostředí      | Bot                                |
| -------------- | ---------------------------------- |
| Mac (dev)      | `@mailagentmacbot` — vlastní token |
| Windows (dev)  | jiný bot — vlastní token           |
| Railway (prod) | produkční bot — vlastní token      |

Nikdy nesdílej token mezi prostředími.

---

### /yes a /no nereagují — blokující async

**Symptom:** Agent čeká na `/yes`, ale příkaz z Telegramu je ignorován.

**Root cause:** `run_check()` blokuje event loop — `wait_for_approval()` drží coroutine, ale Telegram handlery (`cmd_yes`) se nemohou spustit dokud `run_check` neskončí.

**Fix:** Spustit check jako background task:

```python
# ŠPATNĚ — blokuje event loop:
await run_check(context.bot)

# SPRÁVNĚ — neblokuje, handlery fungují:
asyncio.create_task(run_check(context.bot))
```

Platí obecně: každá dlouho běžící operace spuštěná z Telegram handleru musí být `create_task`, jinak Telegram přestane reagovat na příkazy.

---

### Chat ID vs. Bot Token

- **Chat ID** = tvoje osobní Telegram ID — nemění se, platí pro všechny boty
- **Bot Token** = identita konkrétního bota — mění se per prostředí
- Nový bot nezná Chat ID dokud mu nepošleš zprávu (`/start`)

---

### Produkce vs. development — doporučená konfigurace

```
# .env na Mac (dev)
TELEGRAM_BOT_TOKEN=<mac dev bot token>
TELEGRAM_CHAT_ID=<tvoje chat ID>

# .env na Railway (prod)
TELEGRAM_BOT_TOKEN=<produkční bot token>
TELEGRAM_CHAT_ID=<tvoje chat ID>
```
