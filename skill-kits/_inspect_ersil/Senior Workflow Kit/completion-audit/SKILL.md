---
name: completion-audit
description: Independently verify whether an answer, implementation, file, plan, or generated artifact is actually complete. Use before claiming that work is done or when quality matters.
---

# Completion Audit

Audit this claim, result, or deliverable: `$ARGUMENTS`

Do not accept completion at face value. Verify against the original requirement, available evidence, and the strongest checks you can run.

## Audit stance

- Be fair, but skeptical.
- Look for missing requirements, fragile assumptions, silent failures, and untested claims.
- Prefer direct evidence over confidence.
- If you cannot check something, say so clearly.
- Do not rewrite the work unless a narrow fix is obvious and safe; otherwise report the issue and recommended correction.

## Audit checklist

### Requirements match

- What did the user actually ask for?
- Are all requested outputs present?
- Are format, language, tone, file type, and constraints satisfied?
- Are there hidden dependencies or missing inputs?

### Evidence check

- What files, sources, logs, screenshots, tests, docs, or outputs support the result?
- Are referenced paths and artifacts real?
- Are current facts verified when freshness matters?
- Are assumptions labeled?

### Technical verification

For code or data work, run or inspect the best available checks:

- Tests, build, typecheck, lint, formatting.
- Relevant commands and sample inputs.
- File diffs and generated outputs.
- Edge cases, error handling, migrations, config, environment assumptions.

### Content verification

For writing, strategy, research, design, or prompts, check:

- Specificity and usefulness.
- Internal consistency.
- Audience fit.
- Unsupported claims.
- Missing caveats.
- Practical next steps.
- Whether the output is reusable without extra explanation.

### Risk check

Look for:

- Security or privacy leaks.
- Overbroad edits.
- Broken compatibility.
- Hallucinated facts or fake sources.
- Legal/financial/medical overclaiming.
- Brand or reputation risk.

## Verdict scale

- **verified** — requirements are met and key checks passed.
- **partly verified** — usable, but some important checks are missing or risks remain.
- **not verified** — evidence is insufficient, checks failed, or requirements are materially unmet.

## Output format

Return:

- **Verdict**
- **Requirement coverage**
- **Evidence inspected**
- **Checks run**
- **Issues found**
- **Unverified areas**
- **Recommended fix or next check**
