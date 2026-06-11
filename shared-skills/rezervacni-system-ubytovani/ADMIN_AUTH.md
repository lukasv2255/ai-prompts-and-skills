# Admin login systém — rezervační systém (FastAPI)

Doplněk k základnímu rezervačnímu systému (SKILL.md). Místo `OWNER_TOKEN` v URL přidá plnohodnotný admin login s vícenásobnými účty, per-tenant ACL přes slug, bcrypt hesly, signed session cookie, CSRF, rate limit a reset hesla přes email.

**Pozn.:** `OWNER_TOKEN` blokace v host UI (viz SKILL.md) může zůstat — slouží jako rychlá demo pro preview. Admin login je samostatná vrstva pro produkční správu.

## Co umí
- Login (forever cookie — 10 let, sdílený přihlašovací stav mezi zařízeními)
- Více účtů s per-tenant ACL (`slugs: "*"` = super-admin, `slugs: ["chata-x"]` = jen jeden objekt)
- Bootstrap: při prvním startu se vygenerují náhodná hesla a vypíšou do logu (jediná příležitost je vidět)
- Změna hesla z přihlášené relace
- Reset zapomenutého hesla přes email (signed token, 1h TTL) — bez admin zásahu
- Admin dashboard:
  - Tabulka rezervací s tlačítky **Potvrdit / Zrušit / Smazat**
  - Manuální vytvoření rezervace (telefonát, blokace) — rovnou stav `potvrzeno`
- Multi-tenant picker (pokud má účet přístup k víc objektům, vybírá z karet)

## Hardening (zapnuté ve výchozím stavu)
- **CSRF** — double-submit cookie pattern. Mutace přes JSON (`PATCH /potvrdit`, `DELETE`, `POST /admin`) ověřují `X-CSRF-Token` header. HTML formuláře (`/admin/logout`, `/admin/password`) hidden `csrf_token` pole.
- **Rate limit** — slowapi per-IP. `/admin/login` = 5 pokusů / 5 min. `/admin/forgot` = 3 / 10 min.
- **Secure cookies** — automaticky `Secure` flag pod HTTPS (přes `X-Forwarded-Proto` za Railway proxy). HttpOnly na session cookie, čitelná CSRF cookie pro JS.
- **SESSION_SECRET validace** — v produkci (existuje `/data` = Railway volume) refuses boot bez env varu ≥32 znaků.
- **Enumeration-resistant forgot** — vrací stejnou zprávu nezávisle na tom, zda účet existuje.

## Veřejné vs chráněné endpointy
- **Veřejné** (preview a host flow funguje bez loginu): `GET /api/rezervace/{slug}`, `POST /api/rezervace/{slug}` (host vytvoří), `PATCH /api/rezervace/{slug}/{id}/zrusit` (host nebo admin)
- **Chráněné**: `PATCH .../potvrdit`, `DELETE`, `POST /api/rezervace/{slug}/admin`

## Závislosti — přidat do `requirements.txt`
```
bcrypt
itsdangerous
slowapi
```

## Krok 1 — vytvoř `src/auth.py`
Centrální auth modul. Účty + hashe v `data/admin_users.json` lokálně, `/data/admin_users.json` na Railway (persistent volume).

```python
"""
Admin auth — login, bcrypt, signed session cookie, password reset přes email.

Účty + hesla v souboru `data/admin_users.json` (na Railway `/data/admin_users.json`):
{
  "lukas": {"password_hash": "$2b$...", "email": "...", "slugs": "*"},
  "admin": {"password_hash": "$2b$...", "email": "...", "slugs": ["chata-x"]}
}
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import string
from pathlib import Path
from typing import Optional

import bcrypt
from fastapi import Cookie, HTTPException
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

logger = logging.getLogger("rezervace.auth")

_BASE_DIR = Path(__file__).resolve().parent.parent
ADMIN_USERS_FILE = (
    Path("/data/admin_users.json")
    if os.path.exists("/data")
    else _BASE_DIR / "data" / "admin_users.json"
)

SESSION_COOKIE_NAME = "admin_session"
CSRF_COOKIE_NAME = "admin_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"
SESSION_MAX_AGE = 60 * 60 * 24 * 365 * 10  # 10 let
RESET_TOKEN_MAX_AGE = 60 * 60  # 1 hodina
SESSION_SALT = "admin-session-v1"
RESET_SALT = "admin-reset-v1"
CSRF_SALT = "admin-csrf-v1"

# UPRAV: bootstrap účty pro nový projekt
BOOTSTRAP_ACCOUNTS = [
    {"username": "lukas", "email": "tvuj@mail.cz", "slugs": "*"},
    {"username": "admin", "email": "klient@mail.cz", "slugs": ["nazev-slug"]},
]


def _get_secret() -> str:
    secret = os.environ.get("SESSION_SECRET")
    if not secret:
        secret = "DEV-INSECURE-DO-NOT-USE-IN-PROD-" + "x" * 32
        logger.warning("SESSION_SECRET není v env — používám dev fallback")
    return secret


def _session_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(_get_secret(), salt=SESSION_SALT)


def _reset_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(_get_secret(), salt=RESET_SALT)


def validate_session_secret_or_exit() -> None:
    """V produkci (Railway = /data existuje) musí být SESSION_SECRET ≥32 znaků.
    Volá se při importu serveru — chyba shazne deploy."""
    is_production_env = os.path.exists("/data")
    secret = os.environ.get("SESSION_SECRET", "")
    if is_production_env and not secret:
        raise RuntimeError("SESSION_SECRET není nastavený v env. Vygeneruj přes `openssl rand -hex 32`.")
    if is_production_env and len(secret) < 32:
        raise RuntimeError("SESSION_SECRET je příliš krátký (min 32 znaků).")


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def _generate_password(length: int = 16) -> str:
    alphabet = "".join(c for c in (string.ascii_letters + string.digits) if c not in "0O1lI")
    return "".join(secrets.choice(alphabet) for _ in range(length))


def load_users() -> dict:
    if not ADMIN_USERS_FILE.exists():
        return _bootstrap_users()
    try:
        return json.loads(ADMIN_USERS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Chyba čtení %s: %s", ADMIN_USERS_FILE, e)
        return {}


def save_users(users: dict) -> None:
    ADMIN_USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADMIN_USERS_FILE.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")


def _bootstrap_users() -> dict:
    """První spuštění — vygeneruj náhodná hesla a vypiš je."""
    users = {}
    plain_passwords = {}
    for acc in BOOTSTRAP_ACCOUNTS:
        pw = _generate_password()
        plain_passwords[acc["username"]] = pw
        users[acc["username"]] = {
            "password_hash": hash_password(pw),
            "email": acc["email"],
            "slugs": acc["slugs"],
        }
    save_users(users)
    banner = "\n" + "=" * 60 + "\n"
    banner += "ADMIN BOOTSTRAP — uložte si tato hesla, vidíte je naposledy:\n"
    for username, pw in plain_passwords.items():
        banner += f"    {username:10s} / {pw}\n"
    banner += "Hesla si změňte přes /admin/password po prvním přihlášení.\n"
    banner += "=" * 60
    logger.warning(banner)
    print(banner)
    return users


def sign_session(username: str) -> str:
    return _session_serializer().dumps({"u": username})


def verify_session(cookie_value: str) -> Optional[str]:
    if not cookie_value:
        return None
    try:
        data = _session_serializer().loads(cookie_value, max_age=SESSION_MAX_AGE)
        return data.get("u")
    except (BadSignature, SignatureExpired):
        return None
    except Exception:
        return None


def make_reset_token(username: str) -> str:
    return _reset_serializer().dumps({"u": username})


def verify_reset_token(token: str) -> Optional[str]:
    try:
        data = _reset_serializer().loads(token, max_age=RESET_TOKEN_MAX_AGE)
        return data.get("u")
    except (BadSignature, SignatureExpired):
        return None
    except Exception:
        return None


def get_current_user(cookie_value: Optional[str]) -> Optional[dict]:
    if not cookie_value:
        return None
    username = verify_session(cookie_value)
    if not username:
        return None
    users = load_users()
    user = users.get(username)
    if not user:
        return None
    return {"username": username, **user}


def user_can_access_slug(user: dict, slug: str) -> bool:
    slugs = user.get("slugs", [])
    if slugs == "*":
        return True
    if isinstance(slugs, list) and slug in slugs:
        return True
    return False


def require_admin(admin_session: Optional[str] = Cookie(default=None)) -> dict:
    """FastAPI dependency — 401 pokud nepřihlášen. Pro mutace volej navíc verify_csrf."""
    user = get_current_user(admin_session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_admin_for_slug(slug: str, user: dict) -> None:
    if not user_can_access_slug(user, slug):
        raise HTTPException(status_code=403, detail="Forbidden for this slug")


def make_csrf_token() -> str:
    """Náhodný CSRF token (32 bajtů → 43 znaků base64url)."""
    return secrets.token_urlsafe(32)


def verify_csrf(request) -> None:
    """Závislost pro JSON mutace — porovná admin_csrf cookie s X-CSRF-Token header.
    Cross-site útočník nevidí hodnotu cookie → nedoplní správnou hlavičku → 403."""
    cookie_val = request.cookies.get(CSRF_COOKIE_NAME)
    header_val = request.headers.get(CSRF_HEADER_NAME)
    if not cookie_val or not header_val:
        raise HTTPException(status_code=403, detail="CSRF token missing")
    if not secrets.compare_digest(cookie_val, header_val):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")


def verify_csrf_form(form_token: str, cookie_token: Optional[str]) -> None:
    """Pro HTML formuláře — `csrf_token` z body vs cookie."""
    if not form_token or not cookie_token:
        raise HTTPException(status_code=403, detail="CSRF token missing")
    if not secrets.compare_digest(form_token, cookie_token):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
```

## Krok 2 — `src/server.py` doplňky

### Importy
```python
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import sys as _sys_for_auth
_sys_for_auth.path.insert(0, str(Path(__file__).resolve().parent))
import auth  # src/auth.py
auth.validate_session_secret_or_exit()
```

### App setup (před endpointy)
```python
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _is_https(request: Request) -> bool:
    """HTTPS detekce z URL scheme nebo X-Forwarded-Proto (za reverse proxy)."""
    if request.url.scheme == "https":
        return True
    if request.headers.get("x-forwarded-proto", "").lower() == "https":
        return True
    return False


def _set_session_cookie(response, username: str, request: Request):
    """Session cookie (HttpOnly) + CSRF cookie (čitelná pro JS)."""
    secure = _is_https(request)
    response.set_cookie(
        key=auth.SESSION_COOKIE_NAME, value=auth.sign_session(username),
        max_age=auth.SESSION_MAX_AGE, httponly=True, samesite="lax", secure=secure,
    )
    response.set_cookie(
        key=auth.CSRF_COOKIE_NAME, value=auth.make_csrf_token(),
        max_age=auth.SESSION_MAX_AGE, httponly=False, samesite="lax", secure=secure,
    )
```

### Chráněné endpointy (nahradit původní v SKILL.md)
```python
@app.patch("/api/rezervace/{slug}/{rezervace_id}/potvrdit")
def potvrdit_rezervaci(slug: str, rezervace_id: int, request: Request,
                       user: dict = Depends(auth.require_admin)):
    auth.verify_csrf(request)
    auth.require_admin_for_slug(slug, user)
    # ... původní DB logika ...


@app.delete("/api/rezervace/{slug}/{rezervace_id}")
def smazat_rezervaci(slug: str, rezervace_id: int, request: Request,
                     user: dict = Depends(auth.require_admin)):
    """Hard delete — jen admin."""
    auth.verify_csrf(request)
    auth.require_admin_for_slug(slug, user)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        cur = conn.execute("DELETE FROM rezervace WHERE id = ? AND slug = ?",
                           (rezervace_id, slug))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rezervace nenalezena.")
    return {"ok": True}


@app.post("/api/rezervace/{slug}/admin")
def admin_create_rezervace(slug: str, data: RezervaciData, request: Request,
                           user: dict = Depends(auth.require_admin)):
    """Admin vytvoří rezervaci rovnou ve stavu 'potvrzeno' (telefonát, blokace)."""
    auth.verify_csrf(request)
    auth.require_admin_for_slug(slug, user)
    RESERVATIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        konflikt = conn.execute("""
            SELECT id FROM rezervace
            WHERE slug = ? AND pokoj = ? AND stav = 'potvrzeno'
              AND datum_od < ? AND datum_do > ?
        """, (slug, data.pokoj, data.datum_do, data.datum_od)).fetchone()
        if konflikt:
            raise HTTPException(status_code=409, detail="Termín koliduje s jinou potvrzenou rezervací.")
        conn.execute("""
            INSERT INTO rezervace (slug, jmeno, email, telefon, pokoj, datum_od, datum_do, stav, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'potvrzeno', ?)
        """, (slug, data.jmeno, data.email or "", data.telefon or "",
              data.pokoj, data.datum_od, data.datum_do,
              datetime.now(timezone.utc).isoformat()))
    return {"ok": True}
```

### Auth endpointy
```python
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request, info: str | None = None, error: str | None = None):
    return templates.TemplateResponse(request, "admin/login.html",
        {"title": "Přihlášení", "info": info, "error": error})


@app.post("/admin/login")
@limiter.limit("5/5minutes")
def admin_login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    users = auth.load_users()
    user = users.get(username)
    if not user or not auth.verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(request, "admin/login.html",
            {"title": "Přihlášení", "error": "Neplatné jméno nebo heslo."}, status_code=401)
    slugs = user.get("slugs", [])
    target = f"/admin/{slugs[0]}" if (isinstance(slugs, list) and len(slugs) == 1) else "/admin"
    resp = RedirectResponse(url=target, status_code=303)
    _set_session_cookie(resp, username, request)
    return resp


@app.post("/admin/logout")
def admin_logout(request: Request, csrf_token: str = Form(...)):
    auth.verify_csrf_form(csrf_token, request.cookies.get(auth.CSRF_COOKIE_NAME))
    resp = RedirectResponse(url="/admin/login?info=Odhl%C3%A1\u0161eno.", status_code=303)
    resp.delete_cookie(auth.SESSION_COOKIE_NAME)
    resp.delete_cookie(auth.CSRF_COOKIE_NAME)
    return resp


@app.get("/admin/forgot", response_class=HTMLResponse)
def admin_forgot_page(request: Request, info: str | None = None, error: str | None = None):
    return templates.TemplateResponse(request, "admin/forgot.html",
        {"title": "Zapomenuté heslo", "info": info, "error": error})


@app.post("/admin/forgot")
@limiter.limit("3/10minutes")
def admin_forgot_submit(request: Request, username: str = Form(...)):
    # enumeration-resistant — vždy stejná odpověď
    generic_info = "Pokud účet existuje, poslali jsme reset odkaz na evidovaný e-mail."
    users = auth.load_users()
    user = users.get(username.strip())
    if user and user.get("email"):
        token = auth.make_reset_token(username.strip())
        reset_url = f"{PUBLIC_BASE_URL}/admin/reset?token={token}"
        try:
            _send_email(to=user["email"], subject="Reset hesla — admin přístup",
                        html=_build_reset_email_html(username.strip(), reset_url))
        except Exception as e:
            logger.error("Reset email selhal: %s", e)
    return templates.TemplateResponse(request, "admin/forgot.html",
        {"title": "Zapomenuté heslo", "info": generic_info})


@app.get("/admin/reset", response_class=HTMLResponse)
def admin_reset_page(request: Request, token: str):
    username = auth.verify_reset_token(token)
    if not username:
        return templates.TemplateResponse(request, "admin/login.html",
            {"title": "Přihlášení", "error": "Reset odkaz vypršel nebo je neplatný."}, status_code=400)
    return templates.TemplateResponse(request, "admin/reset.html",
        {"title": "Nové heslo", "token": token, "username": username})


@app.post("/admin/reset")
def admin_reset_submit(request: Request, token: str = Form(...),
                       password: str = Form(...), password2: str = Form(...)):
    username = auth.verify_reset_token(token)
    if not username:
        return templates.TemplateResponse(request, "admin/login.html",
            {"title": "Přihlášení", "error": "Reset odkaz vypršel nebo je neplatný."}, status_code=400)
    if password != password2 or len(password) < 8:
        return templates.TemplateResponse(request, "admin/reset.html",
            {"title": "Nové heslo", "token": token, "username": username,
             "error": "Hesla se neshodují nebo jsou kratší než 8 znaků."}, status_code=400)
    users = auth.load_users()
    if username not in users:
        raise HTTPException(status_code=400, detail="Účet neexistuje.")
    users[username]["password_hash"] = auth.hash_password(password)
    auth.save_users(users)
    return RedirectResponse(url="/admin/login?info=Heslo%20zm%C4%9Bn%C4%9Bno.", status_code=303)


@app.get("/admin/password", response_class=HTMLResponse)
def admin_password_page(request: Request, user: dict = Depends(auth.require_admin),
                        info: str | None = None, error: str | None = None):
    return templates.TemplateResponse(request, "admin/password.html",
        {"title": "Změna hesla", "user": user, "info": info, "error": error,
         "csrf_token": request.cookies.get(auth.CSRF_COOKIE_NAME, "")})


@app.post("/admin/password")
def admin_password_submit(request: Request, csrf_token: str = Form(...),
                          old_password: str = Form(...), new_password: str = Form(...),
                          new_password2: str = Form(...),
                          user: dict = Depends(auth.require_admin)):
    auth.verify_csrf_form(csrf_token, request.cookies.get(auth.CSRF_COOKIE_NAME))
    csrf = request.cookies.get(auth.CSRF_COOKIE_NAME, "")
    if not auth.verify_password(old_password, user["password_hash"]):
        return templates.TemplateResponse(request, "admin/password.html",
            {"title": "Změna hesla", "user": user, "error": "Stávající heslo není správně.",
             "csrf_token": csrf}, status_code=400)
    if new_password != new_password2 or len(new_password) < 8:
        return templates.TemplateResponse(request, "admin/password.html",
            {"title": "Změna hesla", "user": user,
             "error": "Hesla se neshodují nebo jsou kratší než 8 znaků.",
             "csrf_token": csrf}, status_code=400)
    users = auth.load_users()
    users[user["username"]]["password_hash"] = auth.hash_password(new_password)
    auth.save_users(users)
    return templates.TemplateResponse(request, "admin/password.html",
        {"title": "Změna hesla", "user": user, "info": "Heslo úspěšně změněno.",
         "csrf_token": csrf})


def _list_all_slugs() -> list[str]:
    """Pro super-admina (slugs == '*') — vypíše všechny slugy z DB."""
    if not RESERVATIONS_DB.exists():
        return []
    with sqlite3.connect(str(RESERVATIONS_DB)) as conn:
        _ensure_rezervace_schema(conn)
        rows = conn.execute("SELECT DISTINCT slug FROM rezervace ORDER BY slug").fetchall()
        return [r[0] for r in rows]


@app.get("/admin", response_class=HTMLResponse)
def admin_picker(request: Request, user: dict = Depends(auth.require_admin)):
    slugs = user.get("slugs", [])
    if slugs == "*":
        slugs = _list_all_slugs()
    elif not isinstance(slugs, list):
        slugs = []
    return templates.TemplateResponse(request, "admin/picker.html",
        {"title": "Vyber chatu", "user": user, "slugs": slugs,
         "csrf_token": request.cookies.get(auth.CSRF_COOKIE_NAME, "")})


@app.get("/admin/{slug}", response_class=HTMLResponse)
def admin_dashboard(slug: str, request: Request, user: dict = Depends(auth.require_admin)):
    auth.require_admin_for_slug(slug, user)
    return templates.TemplateResponse(request, "admin/dashboard.html",
        {"title": f"Admin — {slug}", "user": user, "slug": slug,
         "csrf_token": request.cookies.get(auth.CSRF_COOKIE_NAME, "")})
```

### Pomocná funkce reset emailu
```python
def _build_reset_email_html(username: str, reset_url: str) -> str:
    return f"""\
<div style="font-family:-apple-system,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;background:#fff">
  <div style="background:#0f172a;padding:20px 28px">
    <div style="color:#22c55e;font-size:12px;letter-spacing:1.5px;font-weight:700">ADMIN PŘÍSTUP</div>
    <div style="color:#fff;font-size:20px;font-weight:700;margin-top:4px">Reset hesla</div>
  </div>
  <div style="padding:28px">
    <p style="color:#374151;font-size:15px;line-height:1.6;margin:0 0 16px">
      Někdo (asi vy) požádal o reset hesla pro účet <b>{username}</b>.
      Klikněte na odkaz níže a nastavte si nové heslo. Odkaz platí <b>1 hodinu</b>.
    </p>
    <p style="margin:24px 0">
      <a href="{reset_url}" style="display:inline-block;background:#0f172a;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">
        Nastavit nové heslo →
      </a>
    </p>
    <p style="color:#6b7280;font-size:13px;line-height:1.5;margin:24px 0 0">
      Pokud jste o reset nežádali, tento e-mail ignorujte.
    </p>
  </div>
</div>"""
```

`_send_email(to, subject, html)` musí být v projektu už definováno (typicky Resend integrace).

## Krok 3 — Šablony v `templates/admin/`

### `templates/admin/_base.html`
Sdílený dark-themed base (CSS proměnné, panel, tlačítka, badges, table). Plný obsah viz [referenční implementace v projektu](#reference). Vlož celý soubor; CSS proměnné: `--bg #0f172a`, `--accent #22c55e`, `--danger #ef4444`.

### `templates/admin/login.html`
```html
{% extends "admin/_base.html" %}
{% block content %}
<div class="container-narrow">
  <div class="panel">
    <h1>Přihlášení</h1>
    {% if error %}<div class="msg msg-error">{{ error }}</div>{% endif %}
    {% if info %}<div class="msg msg-info">{{ info }}</div>{% endif %}
    <form method="post" action="/admin/login">
      <label for="username">Jméno účtu</label>
      <input type="text" id="username" name="username" autocomplete="username" required autofocus>
      <label for="password">Heslo</label>
      <input type="password" id="password" name="password" autocomplete="current-password" required>
      <button type="submit" class="btn-block">Přihlásit se</button>
    </form>
    <div class="links"><a href="/admin/forgot">Zapomněl jsem heslo</a></div>
  </div>
</div>
{% endblock %}
```

### `templates/admin/forgot.html`
```html
{% extends "admin/_base.html" %}
{% block content %}
<div class="container-narrow">
  <div class="panel">
    <h1>Zapomenuté heslo</h1>
    <p>Zadej jméno svého účtu. Pokud existuje, pošleme reset odkaz na evidovaný e-mail. Odkaz platí 1 hodinu.</p>
    {% if info %}<div class="msg msg-success">{{ info }}</div>{% endif %}
    <form method="post" action="/admin/forgot">
      <label for="username">Jméno účtu</label>
      <input type="text" id="username" name="username" required autofocus>
      <button type="submit" class="btn-block">Poslat reset odkaz</button>
    </form>
    <div class="links"><a href="/admin/login">← Zpět na přihlášení</a></div>
  </div>
</div>
{% endblock %}
```

### `templates/admin/reset.html`
```html
{% extends "admin/_base.html" %}
{% block content %}
<div class="container-narrow">
  <div class="panel">
    <h1>Nové heslo</h1>
    <p>Nastav si nové heslo pro účet <b>{{ username }}</b>. Minimálně 8 znaků.</p>
    {% if error %}<div class="msg msg-error">{{ error }}</div>{% endif %}
    <form method="post" action="/admin/reset">
      <input type="hidden" name="token" value="{{ token }}">
      <label for="password">Nové heslo</label>
      <input type="password" id="password" name="password" required minlength="8" autofocus>
      <label for="password2">Nové heslo ještě jednou</label>
      <input type="password" id="password2" name="password2" required minlength="8">
      <button type="submit" class="btn-block">Uložit nové heslo</button>
    </form>
  </div>
</div>
{% endblock %}
```

### `templates/admin/password.html`
```html
{% extends "admin/_base.html" %}
{% block content %}
<div class="container-narrow">
  <div class="panel">
    <h1>Změna hesla</h1>
    <p>Přihlášen jako <b>{{ user.username }}</b>. Minimálně 8 znaků.</p>
    {% if error %}<div class="msg msg-error">{{ error }}</div>{% endif %}
    {% if info %}<div class="msg msg-success">{{ info }}</div>{% endif %}
    <form method="post" action="/admin/password">
      <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
      <label for="old_password">Stávající heslo</label>
      <input type="password" id="old_password" name="old_password" required autofocus>
      <label for="new_password">Nové heslo</label>
      <input type="password" id="new_password" name="new_password" required minlength="8">
      <label for="new_password2">Nové heslo ještě jednou</label>
      <input type="password" id="new_password2" name="new_password2" required minlength="8">
      <button type="submit" class="btn-block">Uložit nové heslo</button>
    </form>
    <div class="links"><a href="/admin">← Zpět do adminu</a></div>
  </div>
</div>
{% endblock %}
```

### `templates/admin/picker.html`
```html
{% extends "admin/_base.html" %}
{% block content %}
<div class="container">
  <div class="topbar">
    <div><h1>Vyber chatu ke správě</h1></div>
    <div class="user-info">
      Přihlášen: <b>{{ user.username }}</b> &middot;
      <a href="/admin/password">Změnit heslo</a> &middot;
      <form method="post" action="/admin/logout" style="display:inline">
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
        <button type="submit" class="btn btn-small btn-secondary">Odhlásit</button>
      </form>
    </div>
  </div>
  {% if not slugs %}
    <div class="msg msg-info">Pro tvůj účet zatím nejsou nastavené žádné chaty.</div>
  {% else %}
    {% for s in slugs %}
      <a href="/admin/{{ s }}" class="slug-card">{{ s }}</a>
    {% endfor %}
  {% endif %}
</div>
{% endblock %}
```

### `templates/admin/dashboard.html`
Hlavní obrazovka — tabulka rezervací + form pro ruční vytvoření. CSRF: čte `admin_csrf` cookie a posílá v `X-CSRF-Token` header u všech mutací.

```html
{% extends "admin/_base.html" %}
{% block content %}
<div class="container">
  <div class="topbar">
    <div>
      <h1>{{ slug }}</h1>
      <div style="color: var(--text-muted); font-size: 13px;">Správa rezervací</div>
    </div>
    <div class="user-info">
      <b>{{ user.username }}</b> &middot;
      <a href="/admin">Změnit chatu</a> &middot;
      <a href="/admin/password">Změnit heslo</a> &middot;
      <form method="post" action="/admin/logout" style="display:inline">
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
        <button type="submit" class="btn btn-small btn-secondary">Odhlásit</button>
      </form>
    </div>
  </div>

  <div class="panel" style="margin-bottom: 24px;">
    <h2 style="margin-top: 0;">Vytvořit rezervaci ručně</h2>
    <p>Pro telefonáty nebo blokace termínu. Rezervace se vytvoří rovnou jako <b>potvrzená</b>.</p>
    <form id="admin-create-form" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px 16px; align-items: end;">
      <div><label for="c_jmeno">Jméno</label>
        <input type="text" id="c_jmeno" name="jmeno" required placeholder="Jan Novák nebo 'Blokace — rodina'"></div>
      <div><label for="c_email">E-mail (volitelný)</label>
        <input type="email" id="c_email" name="email"></div>
      <div><label for="c_telefon">Telefon (volitelný)</label>
        <input type="text" id="c_telefon" name="telefon"></div>
      <div><label for="c_pokoj">Pokoj</label>
        <input type="text" id="c_pokoj" name="pokoj" required></div>
      <div><label for="c_datum_od">Příjezd</label>
        <input type="date" id="c_datum_od" name="datum_od" required></div>
      <div><label for="c_datum_do">Odjezd</label>
        <input type="date" id="c_datum_do" name="datum_do" required></div>
      <div style="grid-column: 1 / -1; margin-top: 8px;">
        <button type="submit">Vytvořit potvrzenou rezervaci</button>
        <span id="create-msg" style="margin-left: 12px; font-size: 13px;"></span>
      </div>
    </form>
  </div>

  <div class="panel">
    <h2 style="margin-top: 0;">Všechny rezervace</h2>
    <table>
      <thead>
        <tr><th>Host</th><th>Kontakt</th><th>Pokoj</th><th>Termín</th><th>Stav</th><th>Akce</th></tr>
      </thead>
      <tbody id="rezervace-tbody">
        <tr><td colspan="6" style="text-align:center;color:var(--text-muted)">Načítání…</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script>
const SLUG = {{ slug | tojson }};

// CSRF — admin_csrf cookie je čitelná (není HttpOnly).
// Posíláme ji v X-CSRF-Token u každé mutace.
function getCsrfToken() {
  const m = document.cookie.match(/(?:^|;\s*)admin_csrf=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : '';
}
function csrfHeaders(extra) {
  return Object.assign({'X-CSRF-Token': getCsrfToken()}, extra || {});
}

async function loadRezervace() {
  const tbody = document.getElementById('rezervace-tbody');
  try {
    const res = await fetch(`/api/rezervace/${SLUG}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted)">Žádné rezervace.</td></tr>';
      return;
    }
    tbody.innerHTML = items.map(r => `
      <tr>
        <td>${escapeHtml(r.jmeno)}</td>
        <td>${escapeHtml(r.email || '')}${r.telefon ? '<br><span style="color:var(--text-muted);font-size:12px">' + escapeHtml(r.telefon) + '</span>' : ''}</td>
        <td>${escapeHtml(r.pokoj)}</td>
        <td>${r.datum_od} → ${r.datum_do}</td>
        <td><span class="badge badge-${r.stav}">${r.stav}</span></td>
        <td>
          <div class="row-actions">
            ${r.stav === 'cekajici' ? `<button class="btn-small" onclick="potvrdit(${r.id})">Potvrdit</button>` : ''}
            ${r.stav !== 'zruseno' ? `<button class="btn-small btn-secondary" onclick="zrusit(${r.id})">Zrušit</button>` : ''}
            <button class="btn-small btn-danger" onclick="smazat(${r.id})">Smazat</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--danger)">Chyba: ${e.message}</td></tr>`;
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function potvrdit(id) {
  const res = await fetch(`/api/rezervace/${SLUG}/${id}/potvrdit`, {method: 'PATCH', headers: csrfHeaders()});
  if (!res.ok) { const d = await res.json().catch(() => ({})); alert('Chyba: ' + (d.detail || res.status)); return; }
  loadRezervace();
}

async function zrusit(id) {
  if (!confirm('Zrušit tuto rezervaci?')) return;
  // /zrusit je public — CSRF tu neposíláme
  const res = await fetch(`/api/rezervace/${SLUG}/${id}/zrusit`, {method: 'PATCH'});
  if (!res.ok) { const d = await res.json().catch(() => ({})); alert('Chyba: ' + (d.detail || res.status)); return; }
  loadRezervace();
}

async function smazat(id) {
  if (!confirm('Smazat rezervaci NATRVALO?')) return;
  const res = await fetch(`/api/rezervace/${SLUG}/${id}`, {method: 'DELETE', headers: csrfHeaders()});
  if (!res.ok) { const d = await res.json().catch(() => ({})); alert('Chyba: ' + (d.detail || res.status)); return; }
  loadRezervace();
}

document.getElementById('admin-create-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const msgEl = document.getElementById('create-msg');
  const form = e.target;
  const data = {
    jmeno: form.jmeno.value.trim(), email: form.email.value.trim(),
    telefon: form.telefon.value.trim(), pokoj: form.pokoj.value.trim(),
    datum_od: form.datum_od.value, datum_do: form.datum_do.value,
  };
  const res = await fetch(`/api/rezervace/${SLUG}/admin`, {
    method: 'POST',
    headers: csrfHeaders({'Content-Type': 'application/json'}),
    body: JSON.stringify(data),
  });
  const result = await res.json().catch(() => ({}));
  if (!res.ok) { msgEl.style.color = 'var(--danger)'; msgEl.textContent = 'Chyba: ' + (result.detail || res.status); return; }
  msgEl.style.color = 'var(--accent)'; msgEl.textContent = 'Rezervace vytvořena.';
  form.reset(); loadRezervace();
});

loadRezervace();
</script>
{% endblock %}
```

## Krok 4 — Admin link v patičce preview (volitelné)

V `template.html` (nebo kde máš patičku preview) přidej **neaktivní** link — pro produkci pak odkomentuj `<a>` a smaž `<span>`:
```html
<span>
  <!-- Pro reálné nasazení odkomentuj <a> a smaž <span>. -->
  <span style="opacity:0.5;cursor:default" title="Admin — neaktivní v preview">Admin</span>
  <!-- <a href="/admin/login" style="color:rgba(255,255,255,0.4)">Admin</a> -->
</span>
```

## Krok 5 — Lokální test (před deploym)

```bash
# Spusť server
/opt/homebrew/bin/python3.14 -m uvicorn server:app --app-dir src --port 8765

# Trigger bootstrap (libovolný request na /admin/*)
curl -s http://127.0.0.1:8765/admin/login -o /dev/null

# Bootstrap hesla najdeš v logu — vypadají takto:
# ADMIN BOOTSTRAP — uložte si tato hesla, vidíte je naposledy:
#     lukas      / y3AC3JqgRhrZNbS4
#     admin      / ksuqgx4KoPZqBh3y

# Test CSRF gate (musí vracet 403 bez tokenu)
curl -s -X DELETE http://127.0.0.1:8765/api/rezervace/test/999 -w "\nbez auth: %{http_code}\n"

# Test rate limit (po 5 pokusech musí vracet 429)
for i in {1..7}; do
  curl -s -o /dev/null -w "$i: %{http_code}\n" -X POST \
    -d "username=lukas&password=wrong" http://127.0.0.1:8765/admin/login
done
```

## Krok 6 — Production deploy (Railway)

1. **SESSION_SECRET**: `openssl rand -hex 32` → přidej do Railway env vars jako `SESSION_SECRET`
2. **Persistent volume**: Railway musí mít `/data` mountnutý (admin_users.json zde žije forever)
3. **Smaž lokální `data/admin_users.json`** před commitem (jsou v něm bootstrap hashe z lokálního testu — produkce má vlastní)
4. **`.gitignore`**: přidej `data/admin_users.json`
5. **`PUBLIC_BASE_URL`** env var: veřejná URL projektu (do reset email odkazu)
6. **První deploy**: po startu se v Railway logs objeví bootstrap banner s hesly — ulož si je
7. **Bootstrap účty**: uprav `BOOTSTRAP_ACCOUNTS` v `auth.py` před prvním deploy (jména + emaily klienta)

## Checklist použití v novém projektu
- [ ] `requirements.txt` — přidat `bcrypt`, `itsdangerous`, `slowapi`
- [ ] `src/auth.py` — vytvořit, upravit `BOOTSTRAP_ACCOUNTS`
- [ ] `src/server.py` — přidat importy, limiter, templates, `_is_https`, `_set_session_cookie`, validate při startu
- [ ] Existující `potvrdit_rezervaci` — přidat `Depends(auth.require_admin)` + `verify_csrf` + `require_admin_for_slug`
- [ ] Nové endpointy: `DELETE`, `POST /admin`, `/admin/login`, `/admin/logout`, `/admin/forgot`, `/admin/reset`, `/admin/password`, `/admin`, `/admin/{slug}`
- [ ] Pomocná funkce `_build_reset_email_html` + funkční `_send_email` (Resend / SMTP)
- [ ] `templates/admin/` — všech 7 souborů: `_base.html`, `login`, `forgot`, `reset`, `password`, `picker`, `dashboard`
- [ ] `template.html` (preview) — inert admin link v patičce
- [ ] Lokální test: bootstrap, login, CSRF gate, rate limit
- [ ] Railway env: `SESSION_SECRET`, `PUBLIC_BASE_URL`
- [ ] `.gitignore`: `data/admin_users.json`

## Co se v této session ozkoušelo (lokální verify)
- ✅ Bootstrap vygeneroval `data/admin_users.json` se dvěma účty + náhodnými hesly
- ✅ Login nastavil obě cookies (`admin_session` HttpOnly, `admin_csrf` JS-readable)
- ✅ `DELETE` bez `X-CSRF-Token` → 403; s tokenem → autorizace prošla
- ✅ Rate limit triggeruje 429 po překročení prahu
- ✅ Multi-tenant ACL: `lukas` (`slugs: "*"`) vs `admin` (`slugs: ["chataagata-cz"]`)

## TODO / known limitations
- `PATCH /zrusit` je veřejný (host nebo admin) — v produkci by se mělo scope-nout (email-confirm token)
- `GET /api/rezervace/{slug}` je veřejné a leak-uje PII (jméno, email, telefon hostů) — pro produkci buď gate-nout přes session, nebo odfiltrovat citlivá pole pro nepřihlášené (preview používá ve veřejné tabulce)
