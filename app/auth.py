import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "kr.db"


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


def login_or_create(username: str) -> Optional[int]:
    username = username.strip()
    if len(username) < 3 or len(username) > 32:
        return None
    now = datetime.utcnow().isoformat()
    with connect() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO users (username, created_at) VALUES (?, ?)",
            (username, now),
        )
        uid = cur.lastrowid
        conn.execute(
            "INSERT INTO game_saves (user_id, updated_at) VALUES (?, ?)",
            (uid, now),
        )
        conn.commit()
        return uid