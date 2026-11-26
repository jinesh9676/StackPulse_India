from database.db import query,execute
from auth.security import verify

def login(user,p):
    rows=query('SELECT * FROM users WHERE username=? AND status=\'active\'',(user,))
    return rows[0]['id'] if rows and verify(p,rows[0]['password_hash']) else None

def google_login(sub,email,name):
    rows=query('SELECT * FROM users WHERE google_sub=?',(sub,))
    if rows: return rows[0]['id'] if rows[0]['status']=='active' else None
    if query('SELECT id FROM users WHERE email=?',(email,)): raise ValueError('Email already registered. Use password login; automatic linking is disabled.')
    import secrets
    return execute('INSERT INTO users(full_name,username,email,google_sub) VALUES(?,?,?,?)',(name,'google_'+secrets.token_hex(8),email,sub))
