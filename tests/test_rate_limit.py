from app import app

def test_login_rate_limit():
    client = app.test_client()
    codes = [client.get("/login").status_code for _ in range(6)]
    # Expect 5 redirects (302) then 429
    assert codes[:5] == [302]*5
    assert codes[5] == 429
