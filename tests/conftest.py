import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def start_server():
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,   # ← не блокирует
        stderr=subprocess.DEVNULL,   # ← не блокирует
    )
    for _ in range(30):
        try:
            requests.get(f"{BASE_URL}/api/state", timeout=1)
            break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        process.terminate()
        raise RuntimeError("FastAPI-сервер не запустился за 15 секунд")

    yield process

    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def api_client():
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def reset_state(api_client):
    api_client.post(f"{BASE_URL}/reset", allow_redirects=False)
    yield

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": ["--no-sandbox", "--disable-setuid-sandbox"],
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }