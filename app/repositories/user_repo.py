import sqlite3

from app.domain.exceptions import DomainError
from app.domain.user import Role, User
from app.repositories.base import UserRepository

COLS = "id, username, password_hash, role, active"


def _to_user(row) -> User:
    return User(id=row[0], username=row[1], password_hash=row[2],
                role=Role(row[3]), active=bool(row[4]))


class SqliteUserRepo(UserRepository):
    """All user SQL lives here. Every query uses bound (?) parameters."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get(self, user_id):
        row = self._conn.execute(f"SELECT {COLS} FROM users WHERE id = ?", (user_id,)).fetchone()
        return _to_user(row) if row else None

    def get_by_username(self, username):
        row = self._conn.execute(
            f"SELECT {COLS} FROM users WHERE username = ?", (username,)).fetchone()
        return _to_user(row) if row else None

    def list_all(self):
        rows = self._conn.execute(f"SELECT {COLS} FROM users ORDER BY username").fetchall()
        return [_to_user(r) for r in rows]

    def list_by_role(self, role):
        rows = self._conn.execute(
            f"SELECT {COLS} FROM users WHERE role = ? AND active = 1 ORDER BY username",
            (role.value,)).fetchall()
        return [_to_user(r) for r in rows]

    def count_active_admins(self):
        return self._conn.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'ADMIN' AND active = 1").fetchone()[0]

    def add(self, user):
        try:
            cur = self._conn.execute(
                "INSERT INTO users (username, password_hash, role, active) VALUES (?, ?, ?, ?)",
                (user.username, user.password_hash, user.role.value, int(user.active)))
        except sqlite3.IntegrityError as err:
            raise DomainError("That username is already taken.") from err
        self._conn.commit()
        user.id = cur.lastrowid
        return user

    def update_role(self, user_id, role):
        self._conn.execute("UPDATE users SET role = ? WHERE id = ?", (role.value, user_id))
        self._conn.commit()

    def set_active(self, user_id, active):
        self._conn.execute("UPDATE users SET active = ? WHERE id = ?", (int(active), user_id))
        self._conn.commit()
