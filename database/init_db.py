from database.db import connect


def init():
    with connect() as c:
        c.executescript('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    username TEXT COLLATE NOCASE UNIQUE NOT NULL,
    email TEXT COLLATE NOCASE UNIQUE NOT NULL,
    mobile TEXT,
    password_hash TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'admin')),
    status TEXT NOT NULL DEFAULT 'active',
    goal TEXT,
    risk TEXT,
    google_sub TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    buy_price REAL NOT NULL CHECK(buy_price > 0),
    buy_date TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_symbol TEXT NOT NULL,
    target_price REAL NOT NULL CHECK(target_price > 0),
    alert_type TEXT NOT NULL,
    triggered INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    error_type TEXT,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reset_tokens (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS portfolio_user ON portfolio(user_id);
''')
        c.executemany(
            'INSERT OR IGNORE INTO stocks VALUES (?, ?, ?)',
            [
                (f'{s}.NS', n, k)
                for s, n, k in [
                    ('TCS', 'Tata Consultancy Services', 'IT'),
                    ('INFY', 'Infosys', 'IT'),
                    ('WIPRO', 'Wipro', 'IT'),
                    ('HCLTECH', 'HCLTech', 'IT'),
                    ('TECHM', 'Tech Mahindra', 'IT'),
                    ('HDFCBANK', 'HDFC Bank', 'Banking'),
                    ('ICICIBANK', 'ICICI Bank', 'Banking'),
                    ('SBIN', 'State Bank of India', 'Banking'),
                    ('RELIANCE', 'Reliance Industries', 'Energy'),
                    ('TATASTEEL', 'Tata Steel', 'Industrial'),
                    ('LT', 'Larsen & Toubro', 'Industrial'),
                ]
            ],
        )
