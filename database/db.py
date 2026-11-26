import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB = os.getenv(
    'STACKPULSE_DB',
    str(Path(__file__).resolve().parents[1] / 'stockpulse.db'),
)


@contextmanager
def connect():
    c = sqlite3.connect(DB, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def query(sql, args=()):
    with connect() as c:
        return [dict(r) for r in c.execute(sql, args)]


def execute(sql, args=()):
    with connect() as c:
        return c.execute(sql, args).lastrowid
