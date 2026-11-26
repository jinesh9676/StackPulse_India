from getpass import getpass

from auth.security import hash_password
from database.db import execute
from database.init_db import init


init()

u = input("Admin username: ").strip()
e = input("Admin email: ").strip()
p = getpass("Strong password: ")

if not u or "@" not in e:
    raise ValueError("Invalid username/email")

execute(
    "INSERT INTO users(full_name, username, email, password_hash, role) "
    "VALUES (?, ?, ?, ?, 'admin')",
    ("Owner", u, e, hash_password(p)),
)
print("Admin created")
