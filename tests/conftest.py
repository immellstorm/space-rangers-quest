import importlib

import pytest
import socket
import subprocess
import sys
import time

from pathlib import Path

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    from app import auth, sessions
    importlib.reload(auth)
    importlib.reload(sessions)

    auth.init_db()

    yield tmp_path

@pytest.fixture
def client(temp_db):
    from app import main
    importlib.reload(main)

    from fastapi.testclient import TestClient
    return TestClient(main.app, base_url="https://testserver")


@pytest.fixture
def auth_client(client):
    r = client.post("/login", data={"username": "alice", "pin": "1234"},
                    follow_redirects=False)
    assert r.status_code == 303, f"login failed: {r.status_code} {r.text}"

    r = client.post("/start", data={"player_name": "Тестер"},
                    follow_redirects=False)
    assert r.status_code == 303, f"/start failed: {r.status_code}"

    r = client.post("/quests/select", data={"quest_id": "pirate_lair"},
                    follow_redirects=False)
    assert r.status_code == 303, f"/quests/select failed: {r.status_code}"

    return client

def _wait_for_port(port, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.05)
    return False


@pytest.fixture(scope="function")
def live_server(tmp_path):
    port = _find_free_port()
    env = {
        "PATH": str(Path(sys.executable).parent),
        "DATA_DIR": str(tmp_path),
        "PYTHONPATH": str(Path(__file__).resolve().parent.parent),
        "IS_PROD": "false", 
    }

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        env=env,
        cwd=str(Path(__file__).resolve().parent.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        if not _wait_for_port(port):
            out, err = proc.communicate(timeout=2)
            raise RuntimeError(f"uvicorn не поднялся: {err.decode()}")
        yield f"http://127.0.0.1:{port}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def game_page(live_server, page):
    page.goto(f"{live_server}/login")
    page.fill('input[name="username"]', "tester")
    page.fill('input[name="pin"]', "1234")
    page.get_by_role("button", name="Войти").click()

    page.fill('input[name="player_name"]', "Тестер")
    page.get_by_role("button", name="Начать приключение").click()

    page.get_by_role("button").first.click()

    assert page.locator("#quest-title").count() == 1, \
        f"game_page: не дошли до сцены. URL={page.url}"

    return page