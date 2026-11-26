import re
from database.db import execute
from auth.security import hash_password
GOALS = ['Wealth Creation', 'Retirement', 'Trading', 'Passive Income']
RISKS = ['Conservative', 'Moderate', 'Aggressive']


def register(name, user, email, mobile, p, confirm, goal, risk):
    if (
        not name.strip()
        or not re.fullmatch(r'[A-Za-z0-9_]{3,32}', user)
        or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)
    ):
        raise ValueError('Enter valid name, username and email.')
    if mobile and not re.fullmatch(r'\+?[0-9]{10,15}', mobile):
        raise ValueError('Invalid mobile number')
    if p != confirm:
        raise ValueError('Passwords do not match')
    return execute(
        'INSERT INTO users(full_name, username, email, mobile, password_hash, goal, risk) VALUES(?,?,?,?,?,?,?)',
        (name.strip(), user, email.lower(), mobile, hash_password(p), goal, risk)
    )
