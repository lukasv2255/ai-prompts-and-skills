# Severity Classification

Rate each finding by **realistic impact × ease of exploitation**. When torn
between two levels, state the assumption that tips the decision (e.g. "High if the
endpoint is reachable unauthenticated, Medium if it requires a logged-in user").

## Levels

- **Critical** — Direct, serious compromise with little friction:
  remote code execution; SQL injection exposing/altering the database;
  authentication bypass; unauthenticated trigger of an irreversible side-effect
  (sending mail/money, deleting data); full exposure of secrets or all user data.

- **High** — Serious, but needs some condition:
  authorization bypass / IDOR on sensitive data; stored XSS; injection that
  requires an authenticated (but ordinary) user; hardcoded production credentials;
  prompt injection that can cause an unintended real-world action behind a weak
  guardrail.

- **Medium** — Real but limited:
  needs unusual preconditions, has bounded impact, or requires elevated access;
  reflected XSS; missing rate limiting on auth; sensitive info leak via errors;
  weak crypto where exploitation is non-trivial.

- **Low** — Defense-in-depth / hardening:
  minor info disclosure, missing security headers, verbose errors in non-sensitive
  paths, weak-but-not-exploited randomness.

- **Info** — No direct exploit:
  best-practice notes, code smells, things worth knowing but not vulnerabilities.

## Reporting rules

- Tie severity to the **concrete attacker path**, not the category name. A
  "SQL injection" behind three layers of validation may be Medium, not Critical.
- If you can't confirm exploitability, don't pretend. Use the lower level and note
  what would confirm the higher one.
- Don't inflate to seem thorough; don't downplay a genuine Critical.
- In the summary, give counts per level and name the top 3 to fix first by
  impact-to-effort.
