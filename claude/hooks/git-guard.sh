#!/bin/bash
# Obal kolem block-dangerous-git.sh z claude-leverage (PreToolUse, matcher Bash).
# Force push neblokuje, ale vrátí "ask" — Claude Code se pokaždé zeptá uživatele.
# Vše ostatní (--no-verify, reset --hard na main…) nechá na původním skriptu.
# Vlastní obal místo úpravy claude-leverage: ten je git clone a update by změnu přepsal.

LEVERAGE="$HOME/.local/share/claude-leverage/scripts/hooks/block-dangerous-git.sh"

input=$(cat)

# Stejná detekce jako v původním skriptu: obsah uvozovek je data, ne příkaz.
je_force_push=$(printf '%s' "$input" | python3 -c '
import json, re, sys
cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "") or ""
cmd = re.sub(r"\x27[^\x27]*\x27", " ", cmd)
cmd = re.sub(r"\"(?:[^\"\\]|\\.)*\"", " ", cmd, flags=re.DOTALL).replace("\\", "")
push = re.search(r"git\s+push", cmd)
force = re.search(r"(--force|--force-with-lease|(\s|^)-[A-Za-z]*f[A-Za-z]*(\s|$))", cmd)
print("ano" if push and force else "ne")
' 2>/dev/null)

if [ "$je_force_push" = "ano" ]; then
  cat <<'EOF'
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
 "permissionDecisionReason": "Force push přepíše historii na remote. Potvrď, že to opravdu chceš."}}
EOF
  exit 0
fi

[ -x "$LEVERAGE" ] || exit 0
printf '%s' "$input" | "$LEVERAGE"
