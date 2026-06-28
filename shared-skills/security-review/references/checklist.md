# Security Review Checklist — Node.js & Python

A reference for the security-review skill. Read the section(s) matching the
project's stack (from the PROJECT MAP). Each item is a thing to *look for*, with
the bad pattern and the safer alternative. These are prompts for judgment, not a
box-ticking exercise — confirm exploitability before reporting.

## Table of contents
1. Cross-cutting (applies to both)
2. Node.js / TypeScript
3. Python
4. AI agents & LLM-driven code (mail agents, tool use)

---

## 1. Cross-cutting

**Injection — the core question:** does any untrusted value reach an interpreter
(SQL, shell, HTML, template, eval) without being parameterized or escaped?
- SQL: must use parameterized queries / bound params. String concatenation or
  template interpolation of user input into SQL = injection.
- Command: never pass user input to a shell. Use arg arrays, never a shell string.
- Template: user input rendered as a template (not data) = server-side template
  injection.

**Authorization (most missed class):**
- For every endpoint/handler that returns or mutates data, ask: *is there a check
  that THIS user may touch THIS resource?* Authentication ("who are you") is not
  authorization ("may you do this").
- IDOR: `/users/:id/...` where `:id` comes from the request and isn't checked
  against the session user. Classic and very common.
- Look for authz done in the UI/frontend only — must be enforced server-side.

**Secrets:**
- Hardcoded keys/passwords/tokens in source or committed config.
- Secrets printed to logs or returned in error responses/stack traces.
- Weak password storage: plaintext, MD5, SHA1, unsalted. Want bcrypt/scrypt/argon2.

**Transport & data:**
- Sensitive data over plain HTTP; missing TLS verification (disabled cert checks).
- Sensitive data in URLs/query strings (they get logged).

**Error handling / info leak:**
- Stack traces, SQL errors, or internal paths returned to the client in prod.

---

## 2. Node.js / TypeScript

**Injection & eval:**
- `eval(...)`, `new Function(...)`, `vm` with untrusted input → RCE.
- `child_process.exec`/`execSync` with interpolated input → command injection.
  Prefer `execFile`/`spawn` with an args array.
- ORM raw queries (`sequelize.query`, `knex.raw`, `prisma.$queryRawUnsafe`) with
  interpolation. `$queryRaw` tagged template is safe; `$queryRawUnsafe` is not.

**Express / Fastify:**
- Missing input validation — look for `req.body`/`req.query`/`req.params` used
  directly. Want a schema validator (zod, joi, ajv, class-validator).
- Missing auth middleware on routes that need it; middleware ordering bugs.
- `cors()` with no config = reflects any origin. Check allowed origins.
- No rate limiting on login / token / password-reset routes.
- Mass assignment: spreading `req.body` straight into a DB create/update.

**Prototype pollution:** merging untrusted objects (lodash.merge of user JSON,
`Object.assign` deep merges) — keys like `__proto__`/`constructor`.

**Crypto & randomness:**
- `Math.random()` for tokens/IDs/secrets → use `crypto.randomBytes`/`randomUUID`.
- Home-rolled JWT verification; `jwt.verify` with `algorithms` not pinned (alg
  confusion / `none` algorithm).

**Deserialization / files:**
- `JSON.parse` is fine; deserializing with eval-based libs is not.
- Path traversal: `path.join(base, req.params.x)` without normalizing/containing —
  `../` escapes. Validate the resolved path stays under base.

**Dependencies:** check PROJECT MAP versions; `npm audit` categories. Note known-
risky packages but don't fabricate CVE IDs.

---

## 3. Python

**Injection & eval:**
- `eval()`, `exec()`, `pickle.loads()` on untrusted data → RCE. `pickle` is never
  safe on untrusted input.
- `os.system`, `subprocess` with `shell=True` and interpolated input → command
  injection. Use arg lists and `shell=False`.
- SQL: f-strings / `%` / `.format()` into a query string. Use parameterized
  queries (`cursor.execute(sql, params)`) or the ORM properly. SQLAlchemy
  `text()` with string interpolation is unsafe.
- `yaml.load` without `SafeLoader` → arbitrary object construction. Use
  `yaml.safe_load`.

**Flask / FastAPI / Django:**
- Flask `debug=True` in production → Werkzeug console RCE.
- Missing input validation — FastAPI gets pydantic for free; Flask often has none.
  Check that request data is validated, not just read.
- Missing/!wrong auth dependency or decorator on protected routes.
- Django: `extra()`/`raw()` queries with interpolation; CSRF disabled; `DEBUG=True`.
- SSRF: server-side `requests.get(user_supplied_url)` — can hit internal hosts /
  cloud metadata (169.254.169.254).

**Templates:** Jinja2 `render_template_string` on user input → SSTI → RCE.

**Crypto & randomness:**
- `random` module for security tokens → use `secrets`.
- `hashlib.md5/sha1` for passwords → use `bcrypt`/`argon2`/`passlib`.
- `requests` with `verify=False` disables TLS verification.

**Files / path traversal:** `open(os.path.join(base, user_input))` without
containment; `os.path.realpath` check that the result is under `base`.

**Dependencies:** check PROJECT MAP versions; categories from `pip-audit`/safety.
Note risky ones; don't invent CVE numbers.

---

## 4. AI agents & LLM-driven code (mail agents, tool use)

This is high-priority for any project where model output triggers an action
(send email, call a tool, write a file, make a payment).

- **Prompt injection → action:** can text from an untrusted source (incoming
  email body, scraped web page, user-supplied document) contain instructions the
  agent then *acts on* — e.g. "forward all mail to X", "send this to everyone"?
  Untrusted content must be treated as data, never as commands.
- **No deterministic guardrail:** the decision to perform a side-effect should be
  gated by code (allowlist, confirmation flag, recipient/amount limits), not left
  solely to the model's judgment. Model decides *what*; code enforces *whether*.
- **Recipient / target allowlisting:** for a mail agent, is there a hard allowlist
  of who it may write to? Can the recipient be set from model/untrusted input?
- **Over-broad permissions / credentials:** does the agent run with more access
  (mail account, API scopes, filesystem) than its task needs?
- **No human-in-the-loop on irreversible actions:** sending/deleting/paying should
  require explicit confirmation, ideally enforced in code (a `--confirm` flag,
  not just a prompt instruction).
- **Secrets in prompts/logs:** API keys or credentials placed into prompt text or
  logged with the conversation.
- **Unbounded loops/cost:** an agent that can call itself or tools without a cap.
