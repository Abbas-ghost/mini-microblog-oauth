import sqlite3

con = sqlite3.connect("app.db")
cur = con.cursor()

# Existing posts table (kept as-is; create if missing)
cur.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

# New users table for OAuth logins
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,              -- e.g., 'github', 'google'
    provider_id TEXT NOT NULL,           -- subject/id from the provider
    email TEXT,                          -- may be null if provider doesn’t share
    name TEXT,
    avatar TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(provider, provider_id)
)
""")

con.commit()
con.close()
print("Database initialized/updated.")
