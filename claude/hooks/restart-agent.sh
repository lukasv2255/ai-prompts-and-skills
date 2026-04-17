#!/bin/bash
# PostToolUse hook: po změně .py souboru restartuje main.py
# Platí jen pro mail-agent projekt

PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // ""')

# Reaguj jen na .py soubory
if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Zastav běžící instanci
pkill -f "python3 main.py" 2>/dev/null
sleep 1

# Spusť znovu na pozadí
cd "$PROJECT_DIR" && python3 main.py >> logs/agent.log 2>&1 &

echo "Agent restarted after change: $FILE_PATH" >&2
exit 0
