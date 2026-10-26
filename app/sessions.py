import json
from datetime import datetime
from typing import Optional

from app.auth import connect


def new_state() -> dict:
    return {
        "player_name": "",
        "current_scene": "start",
        "money": 0,
        "relations": {},
        "history": [],
        "inventory": {},
        "trust": {},
        "flags": {},
        "days": 0,
    }


def load_state(user_id: int) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM game_saves WHERE user_id = ?", (user_id,)
        ).fetchone()
    if row is None:
        return new_state()
    return {
        "player_name": row["player_name"],
        "current_scene": row["current_scene"],
        "money": row["money"],
        "days": row["days"],
        "inventory": json.loads(row["inventory"]),
        "trust": json.loads(row["trust"]),
        "flags": json.loads(row["flags"]),
        "history": json.loads(row["history"]),
        "relations": json.loads(row["relations"]),
    }


def save_state(user_id: int, state: dict) -> None:
    now = datetime.utcnow().isoformat()
    with connect() as conn:
        conn.execute("""
            UPDATE game_saves SET
                player_name = ?, current_scene = ?, money = ?, days = ?,
                inventory = ?, trust = ?, flags = ?, history = ?, relations = ?,
                updated_at = ?
            WHERE user_id = ?
        """, (
            state.get("player_name", ""),
            state.get("current_scene", "start"),
            state.get("money", 0),
            state.get("days", 0),
            json.dumps(state.get("inventory", {}), ensure_ascii=False),
            json.dumps(state.get("trust", {}), ensure_ascii=False),
            json.dumps(state.get("flags", {}), ensure_ascii=False),
            json.dumps(state.get("history", []), ensure_ascii=False),
            json.dumps(state.get("relations", {}), ensure_ascii=False),
            now,
            user_id,
        ))
        conn.commit()


def reset_state(user_id: int) -> None:
    now = datetime.utcnow().isoformat()
    with connect() as conn:
        conn.execute("""
            UPDATE game_saves SET
                player_name = '', current_scene = 'start', money = 0, days = 0,
                inventory = '{}', trust = '{}', flags = '{}', history = '[]',
                relations = '{}', updated_at = ?
            WHERE user_id = ?
        """, (now, user_id))
        conn.commit()