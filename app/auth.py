import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import os
DB_PATH = Path(os.environ.get("DATA_DIR", "/data")) / "kr.db"


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                pin_hash TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS game_saves (
                user_id INTEGER PRIMARY KEY,
                player_name TEXT DEFAULT '',
                current_scene TEXT DEFAULT 'start',
                money INTEGER DEFAULT 0,
                days INTEGER DEFAULT 0,
                inventory TEXT DEFAULT '{}',
                trust TEXT DEFAULT '{}',
                flags TEXT DEFAULT '{}',
                history TEXT DEFAULT '[]',
                relations TEXT DEFAULT '{}',
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()

        try:
            conn.execute("ALTER TABLE users ADD COLUMN pin_hash TEXT")
        except sqlite3.OperationalError:
            pass


def _pin_hash(pin: str, salt: str) -> str:
    return hashlib.sha256((salt + pin).encode()).hexdigest()


def login_or_create(username: str, pin: str) -> Optional[int]:
    username = username.strip()
    if len(username) < 3 or len(username) > 32:
        return None
    if not (4 <= len(pin) <= 6) or not pin.isdigit():
        return None

    now = datetime.utcnow().isoformat()
    with connect() as conn:
        row = conn.execute(
            "SELECT id, pin_hash FROM users WHERE username = ?", (username,)
        ).fetchone()

        if row:
            if row["pin_hash"] is None:
                conn.execute(
                    "UPDATE users SET pin_hash = ? WHERE id = ?",
                    (_pin_hash(pin, username), row["id"]),
                )
                conn.commit()
                return row["id"]
            # PIN совпал — пускаем
            if row["pin_hash"] == _pin_hash(pin, username):
                return row["id"]
            # PIN не совпал — отказ
            return None

        cur = conn.execute(
            "INSERT INTO users (username, pin_hash, created_at) VALUES (?, ?, ?)",
            (username, _pin_hash(pin, username), now),
        )
        uid = cur.lastrowid
        conn.execute(
            "INSERT INTO game_saves (user_id, updated_at) VALUES (?, ?)",
            (uid, now),
        )
        conn.commit()
        return uid