import sqlite3, pathlib, datetime

db_path = pathlib.Path("app.db")
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
);
""")
con.commit()
con.close()
print("DB ready at", db_path.resolve())
