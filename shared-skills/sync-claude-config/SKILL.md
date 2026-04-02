---
name: sync-claude-config
description: Synchronizuje globální konfiguraci Clauda (~/.claude/) s git repem ~/ai-prompts-and-skills/claude/. Použij když uživatel napíše "sync claude", "pushni config", "pullni config", "synchronizuj nastavení", nebo "aktualizuj claude config". Podporuje dva módy — push (local → git) a pull (git → local).
---

# Sync Claude Config

Synchronizuje soubory mezi `~/.claude/` a `~/ai-prompts-and-skills/claude/`.

**Soubory k synchronizaci:**
- `CLAUDE.md`
- `settings.json`

**Repo cesta:** `~/ai-prompts-and-skills/`

---

## PUSH mód (local → git)

Použij když uživatel chce uložit aktuální konfiguraci do gitu.

```bash
REPO=~/ai-prompts-and-skills/claude
SRC=~/.claude
CHANGED=()

for f in CLAUDE.md settings.json; do
  if ! diff -q "$SRC/$f" "$REPO/$f" > /dev/null 2>&1; then
    cp "$SRC/$f" "$REPO/$f"
    CHANGED+=("$f")
  fi
done

if [ ${#CHANGED[@]} -eq 0 ]; then
  echo "Vše je aktuální, nic ke commitu."
else
  cd ~/ai-prompts-and-skills
  git add claude/CLAUDE.md claude/settings.json
  git commit -m "Sync Claude config: ${CHANGED[*]}"
  git push
  echo "Pushnuté: ${CHANGED[*]}"
fi
```

## PULL mód (git → local)

Použij když uživatel chce stáhnout konfiguraci z gitu do aktuálního počítače.

```bash
cd ~/ai-prompts-and-skills
git pull

REPO=~/ai-prompts-and-skills/claude
DST=~/.claude
CHANGED=()

for f in CLAUDE.md settings.json; do
  if ! diff -q "$REPO/$f" "$DST/$f" > /dev/null 2>&1; then
    cp "$REPO/$f" "$DST/$f"
    CHANGED+=("$f")
  fi
done

if [ ${#CHANGED[@]} -eq 0 ]; then
  echo "Vše je aktuální, žádné změny."
else
  echo "Aktualizováno: ${CHANGED[*]}"
fi
```

---

## Postup

1. Zjisti z kontextu zda jde o push nebo pull
2. Spusť příslušný bash blok výše
3. Reportuj co bylo změněno (nebo že vše je aktuální)
