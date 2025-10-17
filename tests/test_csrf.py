from app import app

def test_create_rejects_bad_csrf():
    client = app.test_client()
    # simulate logged-in session by setting a csrf token in session
    with client.session_transaction() as sess:
        sess["profile"] = {"id": 123, "login": "testuser"}  # fake login
        sess["csrf_token"] = "goodtoken"
    # send a different token -> expect 400
    resp = client.post("/create", data={"content": "hi", "csrf_token": "badtoken"})
    assert resp.status_code == 400
