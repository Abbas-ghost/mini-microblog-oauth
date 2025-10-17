import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, datetime
import bleach
from authlib.integrations.flask_client import OAuth
import secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

# Cookie hardening
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",  # or "Strict" if you don’t need cross-site OAuth flows
    SESSION_COOKIE_SECURE=False,    # set True in production behind HTTPS
)

# Rate limiting
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

oauth = OAuth(app)
oauth.register(
    name="remote",  # e.g., GitHub/Google – endpoints come from .env
    client_id=os.getenv("OAUTH_CLIENT_ID"),
    client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
    authorize_url=os.getenv("OAUTH_AUTHORIZE_URL"),
    access_token_url=os.getenv("OAUTH_TOKEN_URL"),
    client_kwargs={"scope": "read:user user:email openid profile email"},
)
USERINFO_URL = os.getenv("OAUTH_USERINFO_URL")

# ---- DB helper ----
def get_db():
    con = sqlite3.connect("app.db")
    con.row_factory = sqlite3.Row
    return con

def current_user_id():
    prof = session.get("profile")
    if not prof:
        return None
    provider = "github"
    provider_id = str(prof.get("id"))
    con = get_db()
    row = con.execute(
        "SELECT id FROM users WHERE provider=? AND provider_id=?",
        (provider, provider_id),
    ).fetchone()
    con.close()
    return row["id"] if row else None

# ---- Content Security Policy (defense-in-depth) ----
@app.after_request
def add_csp(resp):
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "img-src 'self' https://avatars.githubusercontent.com data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    )
    return resp

# ---- Allowed HTML for sanitization ----
ALLOWED_TAGS = ["b", "i", "em", "strong", "code", "br", "a"]
ALLOWED_ATTRS = {"a": ["href", "title", "rel"]}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

def ensure_csrf():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token

# ---- Routes ----
@app.get("/")
def index():
    con = get_db()
    posts = con.execute("""
        SELECT p.id, p.content, p.created_at, u.name AS author_name
        FROM posts p
        LEFT JOIN users u ON u.id = p.user_id
        ORDER BY p.id DESC
    """).fetchall()
    con.close()
    return render_template(
        "index.html",
        posts=posts,
        profile=session.get("profile"),
        csrf_token=ensure_csrf(),   # pass CSRF token to template
    )

@app.post("/create")
def create():
    if not session.get("profile"):
        return redirect(url_for("login"))

    # CSRF check
    form_token = request.form.get("csrf_token", "")
    if form_token != session.get("csrf_token"):
        return "Bad CSRF token", 400

    raw = request.form["content"]
    content = bleach.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    content = bleach.linkify(content, skip_tags=["code"])
    uid = current_user_id()
    con = get_db()
    con.execute(
        "INSERT INTO posts (content, created_at, user_id) VALUES (?, ?, ?)",
        (content, datetime.datetime.utcnow().isoformat(), uid),
    )
    con.commit()
    con.close()
    return redirect(url_for("index"))

@limiter.limit("5 per minute")
@app.get("/login")
def login():
    # Send the user to the OAuth provider’s consent page
    redirect_uri = url_for("auth_callback", _external=True)
    return oauth.remote.authorize_redirect(redirect_uri)

@limiter.limit("5 per minute")
@app.get("/auth/callback")
def auth_callback():
    try:
        token = oauth.remote.authorize_access_token()
    except Exception as e:
        print("OAuth token exchange failed:", e)
        return redirect(url_for("login"))

    try:
        resp = oauth.remote.get(USERINFO_URL)
        profile = resp.json()
        if not isinstance(profile, dict) or "id" not in profile:
            raise ValueError("Bad userinfo response")
    except Exception as e:
        print("Fetching user profile failed:", e)
        return redirect(url_for("login"))

    # --- persist user (upsert) ---
    provider = "github"
    provider_id = str(profile.get("id"))
    email = profile.get("email")
    name = profile.get("name") or profile.get("login")
    avatar = profile.get("avatar_url")

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO users (provider, provider_id, email, name, avatar)
        VALUES (?, ?, ?, ?, ?)
    """, (provider, provider_id, email, name, avatar))
    cur.execute("""
        UPDATE users
           SET email = COALESCE(?, email),
               name = COALESCE(?, name),
               avatar = COALESCE(?, avatar)
         WHERE provider = ? AND provider_id = ?
    """, (email, name, avatar, provider, provider_id))
    con.commit()
    con.close()

    session["profile"] = profile
    session["token"] = token
    return redirect(url_for("index"))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# for the earlier demo
@app.get("/steal")
def steal():
    data = request.args.get("c", "")
    print("Stolen data:", data)
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
