#!/bin/bash
# Zkontroluje jestli projekt má Claude šablonu (CLAUDE.md + docs/project_notes)
# Spouští se automaticky při startu každé session

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

missing=()

[ ! -f "$PROJECT_DIR/CLAUDE.md" ] && missing+=("CLAUDE.md")
[ ! -d "$PROJECT_DIR/docs/project_notes" ] && missing+=("docs/project_notes/")
[ ! -d "$PROJECT_DIR/tasks" ] && missing+=("tasks/")
[ ! -d "$PROJECT_DIR/.claude" ] && missing+=(".claude/")

if [ ${#missing[@]} -gt 0 ]; then
  echo "⚠️  Projekt nemá Claude šablonu. Chybí: ${missing[*]}"
  echo "Zkopíruj šablonu z: C:/Users/tommy/claude-code/claude-md/"
  exit 2
fi

exit 0
