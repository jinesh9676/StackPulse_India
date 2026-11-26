import hashlib
import re
import secrets
import time

import bcrypt

from database.db import connect


def validate(p):
    password_rules = (r"[A-Z]", r"[a-z]", r"\d", r"[^\w\s]")
    if (
        not 8 <= len(p) <= 32
        or len(p.encode()) > 72
        or not all(re.search(rule, p) for rule in password_rules)
    ):
        raise ValueError(
            "Password: 8–32 characters, at most 72 UTF-8 bytes, uppercase, "
            "lowercase, number and special character required."
        )


def hash_password(p):
    validate(p)
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify(p, h):
    try:
        return bool(h) and bcrypt.checkpw(p.encode(), h.encode())
    except ValueError:
        return False


def issue_reset(uid):
    token = secrets.token_urlsafe(32)
    with connect() as c:
        c.execute("DELETE FROM reset_tokens WHERE user_id=?", (uid,))
        c.execute(
            "INSERT INTO reset_tokens VALUES(?,?,?)",
            (
                hashlib.sha256(token.encode()).hexdigest(),
                uid,
                int(time.time()) + 900,
            ),
        )
    return token


def reset(token, p):
    h = hash_password(p)
    digest = hashlib.sha256(token.encode()).hexdigest()
    with connect() as c:
        c.execute("BEGIN IMMEDIATE")
        row = c.execute(
            "SELECT user_id FROM reset_tokens "
            "WHERE token_hash=? AND expires>?",
            (digest, int(time.time())),
        ).fetchone()
        if not row:
            raise ValueError("Invalid or expired token")
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (h, row[0]))
        c.execute("DELETE FROM reset_tokens WHERE user_id=?", (row[0],))
