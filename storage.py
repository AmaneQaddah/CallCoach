# storage.py
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(os.getenv("APP_DB_PATH", Path(__file__).resolve().parent / "app.db"))

# New columns (added via lightweight migration)
_EXTRA_COLUMNS = {
    "checklist_score": "INTEGER",
    "checklist_json": "TEXT",
    "customer_type": "TEXT",
    "emotion_level": "INTEGER",
}

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c

def _ensure_columns(con: sqlite3.Connection):
    cols = {r["name"] for r in con.execute("PRAGMA table_info(attempts)").fetchall()}
    for name, sql_type in _EXTRA_COLUMNS.items():
        if name not in cols:
            con.execute(f"ALTER TABLE attempts ADD COLUMN {name} {sql_type}")
    con.commit()

def init_db():
    with _conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_email TEXT NOT NULL,
            mode TEXT NOT NULL,              -- 'training' | 'exam'
            level TEXT NOT NULL,             -- easy|medium|hard
            transcript TEXT NOT NULL,
            score INTEGER,                   -- nullable for training
            passed INTEGER,                  -- 0/1 nullable for training
            summary TEXT,
            strengths TEXT,                  -- JSON string
            improvements TEXT,               -- JSON string
            checklist_score INTEGER,          -- 0-100, nullable
            checklist_json TEXT,              -- JSON string (items/evidence)
            customer_type TEXT,               -- optional
            emotion_level INTEGER             -- optional
        )
        """)
        _ensure_columns(con)

def save_attempt(a: Dict[str, Any]) -> int:
    init_db()
    created_at = a.get("created_at") or datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with _conn() as con:
        cur = con.execute("""
            INSERT INTO attempts(
                created_at,user_email,mode,level,transcript,
                score,passed,summary,strengths,improvements,
                checklist_score,checklist_json,customer_type,emotion_level
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            created_at,
            a["user_email"],
            a["mode"],
            a.get("level", "easy"),
            a.get("transcript", ""),
            a.get("score", None),
            a.get("passed", None),
            a.get("summary", ""),
            a.get("strengths", ""),
            a.get("improvements", ""),
            a.get("checklist_score", None),
            a.get("checklist_json", ""),
            a.get("customer_type", ""),
            a.get("emotion_level", None),
        ))
        con.commit()
        return int(cur.lastrowid)

def list_attempts(limit: int = 200) -> List[Dict[str, Any]]:
    init_db()
    with _conn() as con:
        rows = con.execute("""
            SELECT id, created_at, user_email, mode, level,
                   score, passed, checklist_score
            FROM attempts
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_attempt(attempt_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    with _conn() as con:
        row = con.execute("""
            SELECT *
            FROM attempts
            WHERE id = ?
        """, (attempt_id,)).fetchone()
    return dict(row) if row else None
