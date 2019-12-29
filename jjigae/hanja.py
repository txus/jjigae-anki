import sqlite3
from pathlib import Path
import os

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

path = (ROOT_DIR / "hanjadic.sqlite").resolve()

if not path.exists():
    raise Exception(f"Can't find Hanja DB: {path}")

conn = sqlite3.connect(str(path))

c = conn.cursor()


def lookup(hangeul):
    t = (hangeul,)
    c.execute("SELECT * FROM hanjas WHERE hangul=?", t)
    res = c.fetchone()
    if res is not None:
        return {"hanja": res[0]}
