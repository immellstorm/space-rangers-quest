import pytest

pytestmark = pytest.mark.integration

from tests.test_scenes import make_state

from app.sessions import (
    load_state, new_state, save_state,reset_state
)

from app.auth import (
    login_or_create,  connect
)

from datetime import datetime as real_datetime
import app.sessions

def make_user(temp_db):
    uid = login_or_create("alice", "1234")
    assert uid is not None
    return uid

def test_load_state_for_missing_user(temp_db):
    state = load_state(99999)         
    assert state["current_scene"] == "start"
    assert state["money"] == 0
    assert state["player_name"] == ""
    assert state["inventory"] == {}

def test_load_state_for_missing_user_equals_new_state(temp_db):
    state = load_state(99999)
    assert state == new_state()

def test_save_and_load_roundtrip(temp_db):
    uid = make_user(temp_db)
    
    original = make_state(
        player_name="Вася",
        money=500,
        days=2,
        current_scene="katsap_bar",
        inventory={"bomb": 2, "acid": 1},
        trust={"Kacap": 75},
        flags={"done": True, "count": 3},
        history=["start", "landing"],
    )
    save_state(uid, original)
    loaded = load_state(uid)
    
    assert loaded == original

def test_reset_state_clears_data(temp_db):
    uid = make_user(temp_db)
    save_state(uid, make_state(player_name="Вася", money=500, days=3))
    reset_state(uid)
    
    loaded = load_state(uid)
    assert loaded == new_state()

    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM game_saves WHERE user_id = ?", (uid,)
        ).fetchone()
    assert row["c"] == 1

def test_load_state_without_game_save(temp_db):
    uid = make_user(temp_db)
    with connect() as conn:
        conn.execute("DELETE FROM game_saves WHERE user_id = ?", (uid,))
        conn.commit()
    
    state = load_state(uid)
    assert state == new_state() 

def test_save_state_overwrites(temp_db):
    uid = make_user(temp_db)
    save_state(uid, make_state(money=100))
    save_state(uid, make_state(money=500))
    
    loaded = load_state(uid)
    assert loaded["money"] == 500
    
    with connect() as conn:
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM game_saves WHERE user_id = ?", (uid,)
        ).fetchone()["c"]
    assert count == 1

def test_save_state_updates_timestamp(temp_db, monkeypatch):
    uid = login_or_create("alice", "1234")

    fake_now_1 = real_datetime(2026, 1, 1, 0, 0, 0)

    class FakeDatetime1(real_datetime):
        @classmethod
        def utcnow(cls):
            return fake_now_1

    monkeypatch.setattr(app.sessions, "datetime", FakeDatetime1)
    save_state(uid, make_state(money=100))

    with connect() as conn:
        first = conn.execute(
            "SELECT updated_at FROM game_saves WHERE user_id = ?", (uid,)
        ).fetchone()["updated_at"]
    assert first == "2026-01-01T00:00:00"

    fake_now_2 = real_datetime(2026, 1, 2, 0, 0, 0)

    class FakeDatetime2(real_datetime):
        @classmethod
        def utcnow(cls):
            return fake_now_2

    monkeypatch.setattr(app.sessions, "datetime", FakeDatetime2)
    save_state(uid, make_state(money=200))

    with connect() as conn:
        second = conn.execute(
            "SELECT updated_at FROM game_saves WHERE user_id = ?", (uid,)
        ).fetchone()["updated_at"]
    assert second == "2026-01-02T00:00:00"
    assert first != second 