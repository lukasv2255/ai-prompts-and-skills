---
name: brief-builder
description: Turn vague notes, messy ideas, meeting fragments, client messages, or rough requirements into a precise working brief. Use before implementation, research, creative work, content production, app design, web design, audits, or multi-agent workflows.
---

# Brief Builder

Create a clear working brief from: `$ARGUMENTS`

Use this skill when the input is incomplete, messy, emotional, scattered, or too broad. The goal is to turn raw material into a brief that another model, agent, developer, designer, marketer, researcher, or client could act on without guessing.

Do not over-polish the user's intent into something generic. Preserve the real goal, business context, audience, constraints, and rough edges that matter.

## Core rule

A good brief reduces ambiguity before expensive work begins. It does not pretend that missing information is known.

## Brief-building process

### 1. Extract the real objective

Identify:

- What the user actually wants to achieve.
- Why it matters.
- What should exist at the end.
- Who the output is for.
- What decision, action, or deliverable the brief should enable.

If the user describes a tactic, infer the possible strategic goal and label it as an assumption.

### 2. Separate inputs from interpretation

Create a clean distinction between:

- confirmed facts from the user's material,
- assumptions,
- open questions,
- constraints,
- preferences,
- risks,
- ideas that may be useful but are not yet requirements.

Do not invent names, data, budgets, timelines, laws, product facts, or technical constraints.

### 3. Define success criteria

Make the result measurable or checkable:

- What must the final output include?
- What must it avoid?
- What quality bar should it meet?
- What would make the user reject it?
- What format, length, language, tone, file type, channel, or technical environment matters?

### 4. Find hidden risks and missing context

Look for:

- vague target audience,
- unclear owner or decision-maker,
- missing source material,
- unsupported factual claims,
- brand or legal sensitivity,
- privacy/security issues,
- cost or time constraints,
- dependencies on files, tools, people, APIs, approvals, or live data.

Ask at most one question at the end only if it would materially improve the next step. Otherwise proceed with stated assumptions.

### 5. Recommend the next operating mode

Choose the next command that best fits the task:

- `/precision-mode` for hard, ambiguous, risky, strategic, or high-value work.
- `/task-router` when model cost, effort, or delegation matters.
- `/agent-chain` when several agents or work phases are useful.
- `/completion-audit` when there is already an output to verify.
- `/method-capture` when the goal is to turn a good example into a reusable process.

## Output format

Return the brief in this structure:

### Working brief

- **Goal:**
- **Audience / user:**
- **Desired deliverable:**
- **Context:**
- **Confirmed inputs:**
- **Constraints:**
- **Style / quality bar:**
- **Success criteria:**
- **Risks:**
- **Assumptions:**
- **Open question:**
- **Recommended next command:**

### Ready-to-use task prompt

Write a clean prompt that can be pasted into the next model or command.

### Short version

Write a 3–5 sentence version of the brief for quick sharing with a teammate, client, or stakeholder.

## Behavior notes

- Keep the brief concrete and useful.
- Do not ask a long list of questions.
- Do not convert uncertainty into fake certainty.
- Prefer practical structure over consultant-style language.
- If the user's notes are already clear, preserve them and tighten only what helps execution.
