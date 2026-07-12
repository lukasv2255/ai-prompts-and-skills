---
name: todo
description: Timestamped todo note capture and retrieval. Use when the user says `todo` by itself, asks to `vypis todo`, `vypiš todo`, show, list, summarize, or inspect stored todos, or explicitly asks to write a todo using phrases like `zapis do todo`, `zapiš do todo`, `pridej do todo`, `přidej do todo`, `uloz do todo`, or `ulož do todo`. Stores each todo with a precise local timestamp, a concise bullet summary, and a separate detailed note; default todo listings must show only the concise summary.
---

# Todo

## Storage

Use the nearest project todo file when working inside a project:

```text
tasks/todo.md
```

If there is no clear project context, use the shared global file:

```text
~/ai-prompts-and-skills/tasks/todo.md
```

Create the `tasks/` directory and `todo.md` file if missing. Do not overwrite existing todo content.

## Add a Todo

Add a new todo only when the user explicitly asks to write one, for example:

- `zapis do todo ...`
- `zapiš do todo ...`
- `pridej do todo ...`
- `přidej do todo ...`
- `uloz do todo ...`
- `ulož do todo ...`
- `save to todo ...`
- `add to todo ...`

Do not treat `todo` by itself as a write command.

When adding a todo:

1. Capture the current Europe/Prague local time with minute precision.
2. Format the timestamp as `dd-mm-yyyy HH:MM CET`.
3. Append one entry to `tasks/todo.md`.
4. Include both a concise section and a detailed section.

Use this exact entry shape:

```markdown
## dd-mm-yyyy HH:MM CET - Short title

### Strucne

- One concise bullet.
- Another concise bullet.

### Detail

Longer private note with context, constraints, relevant decisions, and follow-up detail.
```

Keep `Strucne` to a few bullets. Put nuance, reasoning, raw context, and longer notes under `Detail`.

If the user's note is short, infer a compact `Strucne` section and store the original wording in `Detail`. If the user's request includes enough context for detail, preserve that context in `Detail`.

## List Todos

When the user says `todo` by itself, or asks `vypis todo`, `vypiš todo`, `show todo`, `list todos`, or similar, return only:

- timestamp
- short title
- bullets from `### Strucne`

Do not include `### Detail` content in the default listing.

For each item, use a compact shape:

```markdown
- dd-mm-yyyy HH:MM CET - Short title
  - concise bullet
  - concise bullet
```

## Show Details

Only include detailed notes when the user explicitly asks for detail, full todo, exact note, or a specific todo's detail.

When showing details, include the concise section first, then the stored `Detail` section.
