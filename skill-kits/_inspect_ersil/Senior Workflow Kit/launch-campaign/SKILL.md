---
name: launch-campaign
description: Run a complete product/service launch campaign pipeline from raw, incomplete notes to a client-ready plan in one invocation — chains brief-builder, task-router, precision-mode, agent-chain, and completion-audit with cost-aware model routing and two independent audit passes. Use when launching a new product or service (especially B2B) from partial assets, unclear budget, or undefined audience, and the output must survive being shown to a boss or client without embarrassing gaps.
---

# Launch Campaign

Run the full pipeline on: `$ARGUMENTS`

This is not a content-generation skill. It is a discipline for turning thin, unverified material into a campaign plan that doesn't quietly convert assumptions into facts along the way. Use it when the input is a rough ask ("udělej kampaň na X") backed by few confirmed assets and no locked budget or audience.

## Core rule

The plan may only say what the evidence supports. Every gap in the input (audience, budget, market, asset volume) must survive as a visible, labeled gap in the output — not get smoothed over by the third draft.

## Pipeline

Run these stages in order. Do not skip stages to save time — the gate points are where the method actually earns its keep.

### 1. Brief
Invoke `brief-builder` logic on the raw input. Produce: goal, audience, deliverable, confirmed inputs, constraints, style/quality bar, success criteria, risks, assumptions, one open question. Do not invent facts (product name, price, market, certifications) not present in the input. Anything not confirmed is an assumption, labeled as such, not a fact.

### 2. Route
Invoke `task-router` logic. Classify the task band. Assign three roles with explicit model tiers and reasons:
- **Scout** (cheap tier, e.g. haiku) — bounded evidence gathering only (competitors, market, pricing context). Must cite sources. Must not make strategic or creative decisions.
- **Builder** (standard/strong tier, e.g. sonnet) — produces the actual campaign plan from the brief + scout evidence.
- **Auditor** (same tier as builder, but an independent instance/context that never sees the builder's reasoning) — checks the plan against the brief's acceptance criteria only.

Show the routing table to the user before spending on execution.

### 3. Target lock
Invoke `precision-mode`'s target-lock step. Before creating anything, state: desired outcome, acceptance criteria, constraints, unknowns, working assumptions, shortest reliable route. Explicitly list what is unverified. This is a checkpoint, not a formality — if the user corrects it, the correction changes what gets built next.

### 4. Agent-chain plan
Invoke `agent-chain` logic. Write exact worker prompts for scout, builder, and auditor (objective, allowed tools, what not to do, output format, evidence requirement, max scope). Define the handoff format between them and stop conditions (max one correction round after audit, not an open-ended loop). **Show this plan to the user and wait for approval before spawning any agent.** Do not treat "the user approved the pipeline once" as approval for every future run — this gate fires every time real spend (tokens, agent calls) is about to happen.

### 5. Execute
Run scout → builder → auditor in that order, feeding each output into the next as specified in the plan.

Non-negotiable constraints on the builder step, learned from doing this wrong before it was caught:
- Every claim in the plan must trace to a confirmed input or be explicitly marked as a hypothesis/positioning choice, not a product fact.
- Maintain the assumption label everywhere the assumption appears in the document — not just at first mention. A hedge that appears once and vanishes by week 7 of a content calendar is a bug, not style.
- Include an explicit "must not claim" list built from what evidence does NOT cover (e.g. no certifications beyond the one review that exists).
- Never let competitor research become a claim about the user's own product — it's positioning inspiration only.
- CTA must be specific and low-friction, never generic "contact us."
- Structure must be modular against an unconfirmed budget — must work at zero spend and scale up, not assume a number that was never given.

Auditor step: independent instance, checks per stated acceptance criterion with citations from the plan text, verdict PASS / FAIL / HRANIČNÍ (borderline) per criterion. One correction round maximum; apply it directly if narrow, don't re-spawn the builder for a two-line fix.

### 6. Second audit (completion-audit)
Run `completion-audit` as a second, differently-scoped pass — do not let it just re-check the same criteria the first auditor already cleared. Its job is to hunt specifically for:
- Assumptions stated as fact that neither brief-builder's assumption list nor the first auditor caught (market/geography scope, invented numeric benchmarks like budget tiers, resource-volume assumptions like "we have enough photos for 3 series").
- Business/legal/reputational risk nobody raised (e.g. publishing a B2B price list publicly, missing a data-handling line on a lead form).
- Brief requirements that got silently converted from "open question" to "assumption" without ever resurfacing for confirmation.
- **Whether prior corrections actually exist as a persisted artifact**, not just as a description in the conversation. A fix that was described but never written into the document does not count as fixed.

### 7. Persist
Only after the second audit clears (or its findings are applied), write **one consolidated file** with every correction physically applied. The deliverable is that file — not the builder's draft plus a scattered trail of chat-level patch notes. This is the step most likely to get skipped under time pressure; it is also the step that determines whether the output is safe to hand to a boss or client.

## When to use

- A new product/service/feature launch, especially B2B, built from partial material: some assets, no confirmed budget, undefined audience.
- The output will be shown to someone (boss, client) who will notice if a guess is dressed as a fact.

## When not to use

- Trivial single-post content with no strategic stakes — this pipeline is overkill.
- Brief, budget, and audience are already fully confirmed and validated — skip straight to content production.
- Non-marketing engineering or research tasks — use `task-router` / `precision-mode` standalone instead.

## Acceptance criteria

- Working brief exists with fact/assumption/constraint/risk clearly separated.
- Routing table shown with model + reason per role before execution.
- Target lock and unverified list shown before creative work starts.
- Agent-chain plan shown and approved before any agent is spawned.
- Scout output is citation-backed evidence only, no strategy.
- Builder output stays inside confirmed inputs, carries an explicit forbidden-claims list, a specific CTA, and a budget-agnostic modular structure.
- First auditor produces a per-criterion verdict with citations.
- Second audit pass specifically checks for unstated assumptions-as-fact and for whether corrections are persisted.
- Final output exists as a single file with all corrections applied — not spread across chat turns.

## Failure modes to guard against

- Corrections described in chat but never written to a file (this actually happened once — caught only because a second, differently-scoped audit ran).
- Second audit pass rubber-stamping the same criteria the first pass already checked, instead of hunting a different failure class.
- Scout model asked to make a strategic or creative call instead of just gathering cited evidence.
- Auditor spawned from the same context as the builder, biasing it toward agreement instead of independent judgment.
- Skipping the plan-approval gate and spawning paid agent calls before the user has seen and confirmed scope.
- Market/geography or other scope quietly inferred from conversation language (e.g. "user writes in Czech, so target market must be Czech") and then stated as a setting instead of flagged as a guess.
- Numeric benchmarks (budget tiers, KPI targets) invented for the sake of looking concrete, without any basis in the brief.

## Verification / evaluation prompt

Use this to stress-test a completed run of this pipeline:

> Read the final persisted campaign file. For every sentence that states something as fact, trace it to either (a) a confirmed input from the original brief, or (b) an explicit hypothesis/assumption label. Flag any sentence that fails both. Separately, confirm the file exists on disk with all prior audit corrections physically present in the text, not just referenced.

## Example invocation

`/launch-campaign Chceme uvést novou webovou platformu pro účetní firmy na trh v listopadu. Máme demo screenshoty a jeden case study od pilotního zákazníka, rozpočet zatím neznámý, chceme B2B poptávky a aby se o produktu vědělo mezi účetními firmami.`
