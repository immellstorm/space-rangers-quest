import pytest

pytestmark = pytest.mark.integration

from app import auth
from app.auth import (
    login_or_create,  connect
)


def test_db_is_isolated(temp_db):
   assert str(temp_db) in str(auth.DB_PATH)


def test_tables_are_created(temp_db):
    with connect() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    names = {row["name"] for row in rows}
    assert "users" in names
    assert "game_saves" in names


def test_pin_hash_is_deterministic():
    h1 = auth._pin_hash("1234", "alice")
    h2 = auth._pin_hash("1234", "alice")
    assert h1 == h2

def test_pin_hash_changes_with_pin():
    h1 = auth._pin_hash("1234", "alice")
    h2 = auth._pin_hash("4321", "alice")
    assert h1 != h2

def test_pin_hash_changes_with_salt():
    h1 = auth._pin_hash("1234", "alice")
    h2 = auth._pin_hash("1234", "bob")
    assert h1 != h2

def test_pin_hash_is_64_hex_chars():
    h = auth._pin_hash("1234", "alice")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)

def test_pin_hash_matches_known_value():
    assert auth._pin_hash("1234", "alice") == "0771382e88bb08402547cd4bfd0f3a7fc742e9e27fea8889db6207ee23b9c82e"

def test_short_username_returns_none(temp_db):
    assert login_or_create("ab", "1234") is None

    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = 'ab'").fetchone()
    assert row is None

def test_long_username_returns_none(temp_db):
    assert login_or_create("a" * 33, "1234") is None

def test_max_length_username_works(temp_db):
    assert login_or_create("a" * 32, "1234") is not None

@pytest.mark.parametrize("good_pin", ["1234", "123456"])
def test_valid_pin_length_works(good_pin, temp_db):
    assert login_or_create("alice", good_pin) is not None

@pytest.mark.parametrize("bad_pin", ["123", "1234567", "12ab", ""])
def test_invalid_pin_returns_none(bad_pin, temp_db):
    assert login_or_create("alice", bad_pin) is None

def test_new_user_creates_game_save(temp_db):
    uid = login_or_create("alice", "1234")
    assert uid is not None
    with connect() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        save = conn.execute("SELECT * FROM game_saves WHERE user_id = ?", (uid,)).fetchone()
    assert user is not None
    assert user["username"] == "alice"
    assert user["pin_hash"] is not None
    assert save is not None

def test_repeat_login_with_correct_pin(temp_db):
    uid1 = login_or_create("alice", "1234")
    uid2 = login_or_create("alice", "1234")
    assert uid1 == uid2

    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    assert count == 1

def test_repeat_login_with_wrong_pin_returns_none(temp_db):
    uid = login_or_create("alice", "1234")
    assert uid is not None
    assert login_or_create("alice", "9999") is None

    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = 'alice'").fetchone()
    assert row["pin_hash"] == auth._pin_hash("1234", "alice")

def test_username_is_case_insensitive(temp_db):
    uid1 = login_or_create("alice", "1234")
    uid2 = login_or_create("Alice", "1234")
    assert uid1 == uid2 

def test_username_is_stripped(temp_db):
    uid1 = login_or_create("alice", "1234")
    uid2 = login_or_create("  alice  ", "1234")
    assert uid1 == uid2

def test_init_db_is_idempotent(temp_db):
    from app.auth import init_db
    init_db()  
    init_db()