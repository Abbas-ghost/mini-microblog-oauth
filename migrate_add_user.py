import sqlite3

con = sqlite3.connect("app.db")
cur = con.cursor()

# Check if user_id column already exists
cols = [r[1] for r in cur.execute("PRAGMA table_info(posts)").fetchall()]
if "user_id" not in cols:
    cur.execute("ALTER TABLE posts ADD COLUMN user_id INTEGER")  # nullable for old posts
    con.commit()
    print("Added posts.user_id column.")
else:
    print("posts.user_id already exists.")

con.close()
