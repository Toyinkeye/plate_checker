import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "plates.db"


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS plates ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "plate TEXT UNIQUE NOT NULL, "
            "label TEXT DEFAULT '', "
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
        )


def all_plates():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM plates ORDER BY id DESC")]


def find(plate):
    with conn() as c:
        row = c.execute("SELECT * FROM plates WHERE plate = ?", (plate,)).fetchone()
        return dict(row) if row else None


def add(plate, label=""):
    try:
        with conn() as c:
            c.execute("INSERT INTO plates (plate, label) VALUES (?, ?)", (plate, label))
        return find(plate)
    except sqlite3.IntegrityError:
        return None


def remove(plate_id):
    with conn() as c:
        return c.execute("DELETE FROM plates WHERE id = ?", (plate_id,)).rowcount > 0