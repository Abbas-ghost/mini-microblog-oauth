import sqlite3
con = sqlite3.connect("app.db")
con.row_factory = sqlite3.Row
rows = con.execute("""
SELECT p.id, p.user_id, p.created_at,
       substr(p.content,1,40) AS preview,
       u.name AS author
FROM posts p
LEFT JOIN users u ON u.id = p.user_id
ORDER BY p.id DESC
LIMIT 5
""").fetchall()
print([dict(r) for r in rows])
con.close()
