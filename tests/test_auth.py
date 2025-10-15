import os, sys
# add project root to import path (…/Assignment 2)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

def test_post_requires_login():
    client = app.test_client()
    resp = client.post("/create", data={"content": "hi"}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")
