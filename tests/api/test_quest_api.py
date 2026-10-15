import pytest

BASE_URL = "http://127.0.0.1:8000"


def test_api_state_initial(api_client):
    response = api_client.get(f"{BASE_URL}/api/state")

    assert response.status_code == 200
    data = response.json()
    assert data["current_scene"] == "start"
    assert data["money"] == 0
    assert data["relations"] == {}


def test_main_page_returns_html(api_client):
    response = api_client.get(BASE_URL)

    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    assert "Гнездо пиратов" in response.text


def test_static_css_available(api_client):
    response = api_client.get(f"{BASE_URL}/static/css/style.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["Content-Type"]

def test_choose_moves_scene(api_client):
    response = api_client.post(
        f"{BASE_URL}/choose",
        data={"choice_index": 0},
        allow_redirects=False,
    )

    assert response.status_code == 303
    state = api_client.get(f"{BASE_URL}/api/state").json()
    assert state["current_scene"] == "accepted"


def test_choose_invalid_index_returns_500(api_client):
    response = api_client.post(
        f"{BASE_URL}/choose",
        data={"choice_index": 99},
        allow_redirects=False,
    )

    assert response.status_code == 500

def test_reset_returns_to_start(api_client):
    api_client.post(f"{BASE_URL}/choose", data={"choice_index": 0})
    api_client.post(f"{BASE_URL}/choose", data={"choice_index": 0})

    state_before = api_client.get(f"{BASE_URL}/api/state").json()
    assert state_before["current_scene"] == "destroy"

    api_client.post(f"{BASE_URL}/reset")

    state_after = api_client.get(f"{BASE_URL}/api/state").json()
    assert state_after["current_scene"] == "start"
    assert state_after["money"] == 0