---
name: method-capture
description: Turn a strong prior output, session, workflow, prompt, or example into an original reusable skill, slash command, checklist, agent prompt, or evaluation rubric.
---

# Method Capture

Analyze this material or goal: `$ARGUMENTS`

Extract the repeatable operating method behind a good result. Do not copy phrasing from the source material. Preserve the mechanism, judgment, and checks, then express them as a clean reusable workflow.

## What to inspect

Use any available inputs:

- The final output the user liked.
- The original brief or prompt.
- Session notes, decisions, or attempts.
- A weaker output for contrast.
- The target environment where the method will be reused.
- Constraints such as tone, tools, file structure, safety rules, cost, or audience.

If important inputs are missing, infer cautiously and label assumptions.

## Capture process

### 1. Name the real win

Identify what made the result better:

- Accuracy, completeness, speed, originality, structure, tone, design taste, risk control, evidence quality, or practical usefulness.
- Which qualities must be preserved in future outputs?
- Which parts are surface style and which parts are the underlying method?

### 2. Reconstruct the hidden workflow

Infer the repeatable steps:

- How the target was scoped.
- What evidence or context was required.
- Which constraints shaped the result.
- Which checks prevented weak output.
- What judgment calls improved the final quality.
- Which shortcuts are safe and which are dangerous.

### 3. Define activation rules

Specify:

- When the method should run automatically.
- When the user should invoke it manually.
- When it should not be used.
- What inputs improve performance.

### 4. Package the method

Create the most useful reusable artifact:

- Claude Code `SKILL.md`
- Claude app slash command prompt
- Subagent prompt
- Checklist
- Review rubric
- Evaluation prompt
- Team SOP

Use original wording. Do not preserve source-specific names unless they are necessary for the user's workflow.

### 5. Add quality controls

Include:

- Acceptance criteria.
- Failure modes.
- Required evidence.
- Verification steps.
- One stress-test prompt.
- One example invocation.

## Output format

Return:

1. **Extracted method**
2. **When to use it**
3. **Reusable artifact**
4. **Acceptance criteria**
5. **Failure modes**
6. **Verification / evaluation prompt**
7. **Example invocation**
