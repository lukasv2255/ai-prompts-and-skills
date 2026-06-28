---
name: project-analyzer
description: Use this skill to map and understand the structure of a Node.js
  or Python codebase, especially as the FIRST step before a security review.
  It produces a factual PROJECT MAP — languages, frameworks, entry points,
  external input surfaces, dependencies, and the files that touch auth, secrets,
  databases, and side-effects (sending mail, money, deleting data). Trigger this
  whenever the user wants to "understand", "map", "analyze the structure of", or
  "get an overview of" a project or repo, or just before running a security
  review. This skill reports facts only — it does NOT judge code quality or
  hunt for vulnerabilities (that is the security-review skill's job).
---

# Project Analyzer

## Overview

Builds a factual inventory of a Node.js / Python project so that later analysis
(especially a security review) has the context it needs and doesn't waste effort
orienting itself. The output is a **PROJECT MAP**: facts, not opinions.

The mechanical scan is done by `scripts/scan_project.py`. After running it, read
the files it flags to confirm what they actually do, then assemble the map.

## Workflow

1. Determine the project root. If the user hasn't said, ask for the path (or use
   the current working directory if obvious).
2. Run the scanner:
   ```bash
   python3 scripts/scan_project.py <project_root>
   ```
   It auto-detects Node and Python and emits JSON covering: detected languages,
   manifests + dependencies, likely entry points, external input surfaces,
   and files matching sensitive patterns (auth, secrets, DB, network/mail/exec).
3. Read the most important flagged files yourself to confirm the scanner's
   guesses — particularly entry points and anything under "sensitive areas".
   The scanner pattern-matches; you verify meaning.
4. Assemble the PROJECT MAP in the output format below.

## Output format

Emit one Markdown block titled **PROJECT MAP** with these sections:

- **Stack** — languages, runtimes, frameworks detected (with how you know).
- **Entry points** — servers, CLIs, request handlers, cron jobs, agents,
  background workers. Where execution begins.
- **External input surfaces** — *the most important section.* Everywhere
  untrusted data enters: HTTP routes, query/body params, file reads, env vars,
  webhooks, CLI args, and LLM / tool / model outputs that get used downstream.
- **Sensitive areas** — files touching authentication/authorization, secrets/
  credentials, databases, and side-effects (sending email, payments, file
  writes/deletes, shell execution, outbound HTTP).
- **Dependencies of note** — anything outdated or with a name suggesting risk;
  do not assert CVEs you can't verify — flag for the review step instead.
- **Open questions** — anything ambiguous. List it here rather than guessing.

## Rules

- State facts, not fixes. Make **no** vulnerability claims in this skill — that
  is the security-review skill's job. If you spot something alarming, note the
  location under "Sensitive areas" or "Open questions" neutrally.
- When the scanner's guess about a file is unclear, read the file before
  describing it. Don't propagate a wrong guess.
- Keep the map compact and scannable — it is input for the next skill, not a
  final deliverable.
- If the project is neither Node nor Python, say so and produce a best-effort
  map from the directory structure and any manifests you find.
