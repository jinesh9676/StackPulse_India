import os
import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "stockpulse.db"

ADMIN_NAME = "StackPulse Owner"
ADMIN_USERNAME = "owner"
ADMIN_PASSWORD = os.getenv("STOCKPULSE_OWNER_PASSWORD", "jineshah")
ADMIN_EMAIL = os.getenv(
    "STOCKPULSE_OWNER_EMAIL",
    "owner@stackpulse.invalid"
)

USERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    mobile TEXT,
    password_hash TEXT,
    google_sub TEXT UNIQUE,
    role TEXT NOT NULL DEFAULT 'user'
        CHECK(role IN ('admin', 'user')),
    goal TEXT,
    risk TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active', 'blocked', 'inactive')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

SCHEMA = USERS_SCHEMA + """
CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    company_name TEXT,
    quantity REAL NOT NULL CHECK(quantity > 0),
    buy_price REAL NOT NULL CHECK(buy_price >= 0),
    buy_date TEXT,
    brokerage REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    target_price REAL NOT NULL,
    alert_type TEXT NOT NULL
        CHECK(alert_type IN ('Profit', 'Loss', 'Recovery')),
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    used INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    error_type TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
        ON DELETE SET NULL
);
"""

INDEXES = """
CREATE INDEX IF NOT EXISTS idx_users_status
ON users(status);

CREATE INDEX IF NOT EXISTS idx_portfolio_user
ON portfolios(user_id);

CREATE INDEX IF NOT EXISTS idx_portfolio_symbol
ON portfolios(stock_symbol);

CREATE INDEX IF NOT EXISTS idx_alerts_user
ON alerts(user_id);

CREATE INDEX IF NOT EXISTS idx_alerts_status
ON alerts(status);

CREATE INDEX IF NOT EXISTS idx_logs_user
ON logs(user_id);
"""

REQUIRED_COLUMNS = {
    "users": {
        "id", "full_name", "username", "email", "mobile",
        "password_hash", "google_sub", "role", "goal",
        "risk", "status", "created_at"
    },
    "portfolios": {
        "id", "user_id", "stock_symbol", "company_name",
        "quantity", "buy_price", "buy_date", "brokerage",
        "created_at"
    },
    "alerts": {
        "id", "user_id", "stock_symbol", "target_price",
        "alert_type", "status", "created_at"
    },
    "password_resets": {
        "id", "user_id", "token_hash", "expires_at",
        "used", "created_at"
    },
    "settings": {"key", "value"},
    "logs": {
        "id", "user_id", "error_type",
        "description", "created_at"
    }
}


def print_header(message):
    print("=" * 60)
    print(message)
    print("=" * 60)


def connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def get_columns(conn, table):
    rows = conn.execute(
        f'PRAGMA table_info("{table}")'
    ).fetchall()

    return {row["name"] for row in rows}


def table_exists(conn, table):
    return conn.execute(
        """
        SELECT 1 FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table,)
    ).fetchone() is not None


def backup_database():
    if not DB_PATH.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = ROOT / f"stockpulse_backup_{timestamp}.db"

    source = sqlite3.connect(DB_PATH)
    target = sqlite3.connect(backup_path)

    try:
        source.backup(target)
        print(f"[BACKUP] {backup_path.name}")

    finally:
        target.close()
        source.close()


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, password_hash):
    if not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    except (ValueError, TypeError, AttributeError):
        return False


def migrate_users(conn):
    if not table_exists(conn, "users"):
        return

    row = conn.execute(
        """
        SELECT sql FROM sqlite_master
        WHERE type = 'table' AND name = 'users'
        """
    ).fetchone()

    schema = row["sql"] or ""

    if "'owner'" not in schema.lower():
        return

    columns = get_columns(conn, "users")
    required = REQUIRED_COLUMNS["users"]

    if missing := required - columns:
        names = ", ".join(sorted(missing))
        raise RuntimeError(f"Missing users columns: {names}")

    if extra := columns - required:
        names = ", ".join(sorted(extra))
        raise RuntimeError(f"Unexpected users columns: {names}")

    objects = conn.execute(
        """
        SELECT sql FROM sqlite_master
        WHERE tbl_name = 'users'
        AND type IN ('index', 'trigger')
        AND sql IS NOT NULL
        """
    ).fetchall()

    new_schema = USERS_SCHEMA.replace(
        "IF NOT EXISTS users",
        "users_new",
        1
    )

    conn.execute(new_schema)

    conn.execute(
        """
        INSERT INTO users_new (
            id,
            full_name,
            username,
            email,
            mobile,
            password_hash,
            google_sub,
            role,
            goal,
            risk,
            status,
            created_at
        )
        SELECT
            id,
            full_name,
            username,
            COALESCE(
                NULLIF(TRIM(email), ''),
                'legacy-' || id || '@stackpulse.invalid'
            ),
            mobile,
            password_hash,
            google_sub,
            CASE
                WHEN role = 'owner' THEN 'admin'
                ELSE role
            END,
            goal,
            risk,
            COALESCE(status, 'active'),
            created_at
        FROM users
        """
    )

    conn.execute("DROP TABLE users")
    conn.execute("ALTER TABLE users_new RENAME TO users")

    for item in objects:
        conn.execute(item["sql"])

    print("[UPDATED] Legacy owner role converted to admin")


def migrate_alerts(conn):
    columns = get_columns(conn, "alerts")

    if "status" not in columns:
        conn.execute(
            """
            ALTER TABLE alerts
            ADD COLUMN status TEXT DEFAULT 'active'
            """
        )

        print("[UPDATED] alerts.status")

    if "created_at" not in columns:
        conn.execute(
            """
            ALTER TABLE alerts
            ADD COLUMN created_at DATETIME
            """
        )

        conn.execute(
            """
            UPDATE alerts
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
            """
        )

        print("[UPDATED] alerts.created_at")

    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_alerts_created_at
        AFTER INSERT ON alerts
        FOR EACH ROW
        WHEN NEW.created_at IS NULL
        BEGIN
            UPDATE alerts
            SET created_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END
        """
    )


def validate_schema(conn):
    for table, required in REQUIRED_COLUMNS.items():
        columns = get_columns(conn, table)

        if missing := required - columns:
            names = ", ".join(sorted(missing))

            raise RuntimeError(
                f"Incompatible table '{table}': {names}"
            )

    if conn.execute(
        """
        SELECT COUNT(*) FROM users
        WHERE role IS NULL
        OR role NOT IN ('admin', 'user')
        """
    ).fetchone()[0]:

        raise RuntimeError("Invalid user roles detected.")

    print("[OK] Database schema validated")


def create_indexes(conn):
    for statement in INDEXES.split(";"):
        if statement.strip():
            conn.execute(statement)

    print("[OK] Database indexes")


def create_admin(conn):
    admin = conn.execute(
        """
        SELECT id, role, status, email, password_hash
        FROM users
        WHERE username = ? COLLATE NOCASE
        """,
        (ADMIN_USERNAME,)
    ).fetchone()

    if admin is None:
        if conn.execute(
            """
            SELECT id FROM users
            WHERE email = ? COLLATE NOCASE
            """,
            (ADMIN_EMAIL,),
        ).fetchone():
            raise RuntimeError(
                "Administrator email belongs to another account."
            )

        conn.execute(
            """
            INSERT INTO users (
                full_name,
                username,
                email,
                mobile,
                password_hash,
                role,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ADMIN_NAME,
                ADMIN_USERNAME,
                ADMIN_EMAIL,
                "",
                hash_password(ADMIN_PASSWORD),
                "admin",
                "active"
            )
        )

        print("[CREATED] Administrator account")
        return

    if admin["role"] != "admin":
        raise RuntimeError(
            "Existing owner username is not an administrator."
        )

    if not admin["email"]:
        conn.execute(
            """
            UPDATE users
            SET email = ?
            WHERE id = ?
            """,
            (
                ADMIN_EMAIL,
                admin["id"]
            )
        )

        print("[UPDATED] Administrator email")

    if not admin["password_hash"]:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
            """,
            (
                hash_password(ADMIN_PASSWORD),
                admin["id"]
            )
        )

        print("[UPDATED] Administrator password initialized")

    print("[EXISTS] Administrator account")


def create_settings(conn):
    conn.execute(
        """
        INSERT OR IGNORE INTO settings(key, value)
        VALUES ('notice', '')
        """
    )

    print("[OK] Default settings")


def validate_foreign_keys(conn):
    if violations := conn.execute("PRAGMA foreign_key_check").fetchall():
        raise RuntimeError(
            f"Foreign key violations: {len(violations)}"
        )

    print("[OK] Foreign key integrity")


def validate_database(conn):
    result = conn.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    if result != "ok":
        raise RuntimeError(f"Database integrity error: {result}")

    print("[OK] SQLite integrity check")


def show_tables(conn):
    tables = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()

    print_header("DATABASE TABLES")

    for table in tables:
        print(f"[OK] {table['name']}")

    print("-" * 60)
    print(f"[TOTAL] {len(tables)} tables")


def show_admin(conn):
    admin = conn.execute(
        """
        SELECT username, email, role, status, password_hash
        FROM users
        WHERE username = ? COLLATE NOCASE
        """,
        (ADMIN_USERNAME,)
    ).fetchone()

    if not admin:
        return

    print_header("ADMINISTRATOR ACCOUNT")

    print(f"[USERNAME] {admin['username']}")
    print(f"[EMAIL] {admin['email']}")
    print(f"[ROLE] {admin['role']}")
    print(f"[STATUS] {admin['status']}")
    print("[PASSWORD] Stored securely using bcrypt")
    print("[ROLES] admin, user")

    if verify_password(ADMIN_PASSWORD, admin["password_hash"]):
        print("[OK] Default administrator credentials verified")

    else:
        print("[INFO] Existing administrator password preserved")


def apply_schema(conn):
    for statement in SCHEMA.split(";"):
        if statement.strip():
            conn.execute(statement)

    migrate_users(conn)
    migrate_alerts(conn)
    validate_schema(conn)
    create_indexes(conn)


def prepare_database(conn):
    apply_schema(conn)
    create_admin(conn)
    create_settings(conn)
    validate_foreign_keys(conn)
    validate_database(conn)


def initialize_database(conn):
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("BEGIN IMMEDIATE")

    prepare_database(conn)

    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")

    print("[READY] SQLite database")
    print(f"[PATH] {DB_PATH}")

    show_tables(conn)
    show_admin(conn)


def init():
    print_header("StackPulse India - SQLite Database")
    print("[SQLite] Installing database...")

    backup_database()

    conn = connect()

    try:
        initialize_database(conn)

    except BaseException:
        conn.rollback()
        raise

    finally:
        conn.close()

    print_header("[SUCCESS] Database initialization completed")


def query(sql, params=()):
    conn = connect()

    try:
        return conn.execute(sql, params).fetchall()

    finally:
        conn.close()


def execute(sql, params=()):
    conn = connect()

    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    try:
        init()

    except KeyboardInterrupt:
        print("\n[STOPPED] Installation cancelled.")
        raise SystemExit(130) from None

    except Exception as error:
        print(f"[ERROR] {error}")
        print("[FAILED] Database initialization unsuccessful.")
        raise SystemExit(1) from None
