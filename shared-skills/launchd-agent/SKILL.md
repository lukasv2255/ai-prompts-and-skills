# Skill: launchd-agent

Správa Python agenta přes launchd na macOS — start, stop, restart, reinstalace.

Použij kdykoliv uživatel říká:

- "restartuj agenta", "zastav agenta", "spusť agenta"
- "reinstaluj launchd", "aktualizuj plist"
- "jak spustit/zastavit agenta na Macu"

---

## Základní příkazy

```bash
# Start
launchctl start com.mailagent.agent

# Stop (trvalý — agent zůstane zastavený)
launchctl stop com.mailagent.agent

# Restart (kill + start atomicky)
launchctl kickstart -k gui/$(id -u)/com.mailagent.agent

# Status
launchctl list | grep mailagent
```

### Výstup `launchctl list`:

- `PID = číslo` → agent běží
- `PID = -` + `LastExitStatus = 0` → zastaven normálně
- `PID = -` + `LastExitStatus ≠ 0` → spadl

---

## Reinstalace plistu (po každé změně souboru)

```bash
launchctl unload ~/Library/LaunchAgents/com.mailagent.plist
cp launchd/com.mailagent.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.mailagent.plist
launchctl start com.mailagent.agent
```

> Změna plistu se neprojeví bez unload + load.

---

## Aktuální stav (mail-agent, duben 2026)

Plist má `KeepAlive: true`. Důsledky:

- Agent se restartuje při pádu ✓
- `launchctl stop` ho launchd znovu nastartuje — nelze trvale zastavit bez `unload` ✗
- Pokud uživatel spustí `python3 main.py` ručně zatímco launchd běží → dvě instance, 409 Conflict od Telegramu, duplicitní newslettery

---

## Jak zabránit dvěma instancím — 2 varianty

### Varianta A: KeepAlive `SuccessfulExit: false` (doporučeno)

Změna pouze v plistu, bez úpravy kódu. Launchd sám garantuje jednu instanci.

**Výhody:** jednoduché, žádný kód
**Nevýhody:** `python3 main.py` ručně stále může vytvořit druhou instanci

### Varianta B: PID lock soubor v kódu

Agent zapíše PID do `agent.pid` při startu, při ukončení soubor smaže. Druhá instance zkontroluje soubor a pokud proces s daným PID běží, okamžitě skončí s chybou v logu.

**Výhody:** funguje bez ohledu na to jak byl agent spuštěn (launchd i ručně)
**Nevýhody:** vyžaduje úpravu `main.py`, při tvrdém pádu může zůstat zastaralý `agent.pid`

Implementace do `main.py`:

```python
import atexit, os, sys

PID_FILE = "agent.pid"

def _acquire_pid_lock():
    if os.path.exists(PID_FILE):
        old_pid = int(open(PID_FILE).read().strip())
        try:
            os.kill(old_pid, 0)   # 0 = jen zkontroluj, nezabíjej
            print(f"[ERROR] Jiná instance běží (PID {old_pid}). Ukončuji.", flush=True)
            sys.exit(1)
        except ProcessLookupError:
            pass   # starý PID je mrtvý, pokračujeme
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    atexit.register(lambda: os.remove(PID_FILE) if os.path.exists(PID_FILE) else None)

# Zavolat jako první řádek main():
_acquire_pid_lock()
```

Při tvrdém pádu (SIGKILL) `atexit` neběží → `agent.pid` zůstane. Launchd restartuje → nový proces zjistí, že starý PID je mrtvý → přepíše soubor → OK.

---

## KeepAlive možnosti v plistu

### 1. `true` — vždy restartovat (aktuální stav mail-agent)

```xml
<key>KeepAlive</key>
<true/>
```

- Restartuje při pádu ✓
- Restartuje i po `launchctl stop` ✗ → `stop` nefunguje jako skutečný stop
- Může způsobit souběžné instance pokud uživatel spustí proces ručně

### 2. `false` — nikdy nerestartovat

```xml
<key>KeepAlive</key>
<false/>
```

- Při pádu se agent nespustí → nutný ruční start
- `launchctl stop` funguje trvale ✓
- Vhodné pokud chceš plnou ruční kontrolu

### 3. `SuccessfulExit: false` — restartovat jen při pádu ✅ doporučeno

```xml
<key>KeepAlive</key>
<dict>
    <key>SuccessfulExit</key>
    <false/>
</dict>
```

- Restartuje při pádu (exit code ≠ 0) ✓
- `launchctl stop` funguje trvale (exit code = 0) ✓
- Nejlepší pro produkci — auto-recover při pádu, ale ovladatelný

---

## Pravidlo: jedna instance

`launchctl start` je idempotentní — pokud agent už běží, launchd ho nespustí podruhé.
**Nikdy nespouštěj `python3 main.py` ručně pokud běží launchd** — vzniknou dvě instance se stejným Telegram tokenem (409 Conflict) a obě budou posílat duplicitní zprávy/newslettery.

Jak zjistit kolik instancí běží:

```bash
ps aux | grep "main.py" | grep -v grep
```

---

## Logy

```bash
# Stdout (info logy)
tail -f logs/agent.log

# Stderr (chyby, stack traces)
tail -f logs/agent_err.log

# Uptime záznamy (start/stop/pády)
cat logs/uptime.jsonl
```

Pozor: pokud má agent v kódu `FileHandler("logs/agent.log")` A launchd má `StandardOutPath` na stejný soubor → každý log řádek se zapíše dvakrát. Řešení: v kódu používej pouze `StreamHandler`, logování do souboru nechej na launchd.
