import pytest

pytestmark = pytest.mark.integration

def test_client_can_connect(client):
    r = client.get("/login")
    assert r.status_code == 200


def test_auth_client_has_session(auth_client):
    r = auth_client.get("/api/state")
    assert r.status_code == 200
    data = r.json()
    assert data["player_name"] == "Тестер"
    assert data["current_scene"] == "start"

def test_login_page_renders(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert "PIN" in r.text

def test_root_redirects_to_login_if_not_logged_in(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"

def test_login_success_redirects_and_sets_cookie(client):
    r = client.post("/login", data={"username": "bob", "pin": "5678"},
                    follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"
    assert "session" in r.cookies or "session" in client.cookies

def test_login_wrong_pin_returns_400(client):
    client.post("/login", data={"username": "carol", "pin": "1234"})

    r = client.post("/login", data={"username": "carol", "pin": "9999"},
                    follow_redirects=False)
    assert r.status_code == 400

def test_api_state_unauthorized(client):
    r = client.get("/api/state")
    assert r.status_code == 401

def test_api_state_authorized(auth_client):
    r = auth_client.get("/api/state")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "current_scene" in data
    assert "inventory" in data

def test_choose_advances_scene(auth_client):
    before = auth_client.get("/api/state").json()
    assert before["current_scene"] == "start"

    r = auth_client.post("/choose", data={"choice_index": 0},
                        follow_redirects=False)
    assert r.status_code == 303

    after = auth_client.get("/api/state").json()
    assert after["current_scene"] == "landing"

def test_choose_invalid_index(auth_client):
    with pytest.raises(IndexError, match="Неверный индекс"):
        auth_client.post("/choose", data={"choice_index": 999},
                         follow_redirects=False)

def test_glossary_page(client):
    r = client.get("/glossary")
    assert r.status_code == 200
    assert "Пеленги" in r.text

def test_logout_clears_session(auth_client):
    r = auth_client.post("/logout", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"

    r = auth_client.get("/api/state")
    assert r.status_code == 401

def test_first_creates_user_with_money(auth_client):
    auth_client.post("/choose", data={"choice_index": 0})
    state = auth_client.get("/api/state").json()
    assert state["current_scene"] == "landing"

def test_second_starts_fresh(auth_client):
    state = auth_client.get("/api/state").json()
    assert state["current_scene"] == "start"  