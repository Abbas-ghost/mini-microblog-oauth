\# Mini Microblog — XSS Demo (Flask + SQLite)



\## Setup

1\) Create venv and activate (Windows PowerShell):

&nbsp;  - `py -3 -m venv .venv`

&nbsp;  - `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

&nbsp;  - `. .\\.venv\\Scripts\\Activate.ps1`

2\) Install deps: `pip install -r requirements.txt`

3\) Init DB (one time): `py init\_db.py`

4\) Run: `py app.py` → open http://127.0.0.1:5000



\## What it demonstrates

\- Stored XSS (intentionally added earlier during demo) and fixes:

&nbsp; - Safe templating (no `| safe` on untrusted data)

&nbsp; - Input sanitization with `bleach` allow-list

&nbsp; - Content Security Policy (CSP) header



\## Files

\- `app.py` — app routes, CSP, sanitization

\- `templates/index.html` — form + post list

\- `init\_db.py` — creates `app.db`

\- `app.db` — SQLite database (created at runtime)



