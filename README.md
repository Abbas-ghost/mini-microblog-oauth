# Mini Microblog (OAuth)

## Setup
1) Create venv and install deps:
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

2) Create `.env`:
   FLASK_APP=app.py
   FLASK_DEBUG=1
   SECRET_KEY=change-me
   OAUTH_CLIENT_ID=...        # GitHub
   OAUTH_CLIENT_SECRET=...
   OAUTH_AUTHORIZE_URL=https://github.com/login/oauth/authorize
   OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
   OAUTH_USERINFO_URL=https://api.github.com/user

3) Initialize DB:
   python init_db.py
   python migrate_add_user.py

## Run
python app.py
