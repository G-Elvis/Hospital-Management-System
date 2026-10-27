from app.domain.exceptions import AuthenticationError
from app.domain.user import User
from app.repositories.base import UserReader
from app.security.password_hasher import PasswordHasher


class AuthService:


    def __init__(self, users: UserReader, hasher: PasswordHasher):
        self._users = users
        self._hasher = hasher

    def login(self, username: str, password: str) -> User:
        user = self._users.get_by_username((username or "").strip())

        if (user is None or not user.active
                or not self._hasher.verify(password or "", user.password_hash)):
            raise AuthenticationError("Invalid username or password.")
        return user

    def get_user(self, user_id: int) -> User | None:
        return self._users.get(user_id)
