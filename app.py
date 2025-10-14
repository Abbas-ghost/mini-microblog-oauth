from flask import Flask, render_template, request, redirect, url_for
import sqlite3, datetime
import bleach

app = Flask(__name__)

# ---- DB helper ----
def get_db():
    con = sqlite3.connect("app.db")
    con.row_factory = sqlite3.Row
    return con

# ---- Content Security Policy (defense-in-depth) ----
@app.after_request
def add_csp(resp):
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    )
    return resp

# ---- Allowed HTML for sanitization ----
ALLOWED_TAGS = ["b", "i", "em", "strong", "code", "br", "a"]
ALLOWED_ATTRS = {"a": ["href", "title", "rel"]}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

# ---- Routes ----
@app.get("/")
def index():
    con = get_db()
    posts = con.execute(
        "SELECT id, content, created_at FROM posts ORDER BY id DESC"
    ).fetchall()
    con.close()
    return render_template("index.html", posts=posts)

@app.post("/create")
def create():
    raw = request.form["content"]
    content = bleach.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    content = bleach.linkify(content, skip_tags=["code"])
    con = get_db()
    con.execute(
        "INSERT INTO posts (content, created_at) VALUES (?, ?)",
        (content, datetime.datetime.utcnow().isoformat()),
    )
    con.commit()
    con.close()
    return redirect(url_for("index"))

# for the earlier demo
@app.get("/steal")
def steal():
    data = request.args.get("c", "")
    print("Stolen data:", data)
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

