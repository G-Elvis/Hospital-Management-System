from app.domain.exceptions import DomainError, NotFound, ValidationError
from app.domain.user import Role, User
from app.repositories.base import UserRepository
from app.security.password_hasher import PasswordHasher

MIN_PASSWORD_LENGTH = 8


class AdminService:
    """Staff-account administration (FR-ADM-01..04)."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher):
        self._users = users
        self._hasher = hasher

    def list_users(self):
        return self._users.list_all()

    def create_user(self, username: str, password: str, role) -> User:
        errors = []
        if not username or not username.strip():
            errors.append("Username is required.")
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        try:
            role = Role(role)
        except ValueError:
            errors.append("Select a valid role.")
        if errors:
            raise ValidationError(errors)
        user = User(None, username.strip(), self._hasher.hash(password), role)
        return self._users.add(user)       # repository rejects duplicate usernames

    def _get(self, user_id: int) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise NotFound("User not found.")
        return user

    def _guard_last_admin(self, target: User):
        if target.role == Role.ADMIN and target.active and self._users.count_active_admins() <= 1:
            raise DomainError("You cannot remove the only active administrator.")

    def deactivate(self, user_id: int) -> None:
        target = self._get(user_id)
        self._guard_last_admin(target)
        self._users.set_active(user_id, False)

    def change_role(self, user_id: int, role) -> None:
        target = self._get(user_id)
        try:
            role = Role(role)
        except ValueError as err:
            raise ValidationError(["Select a valid role."]) from err
        if role != Role.ADMIN:
            self._guard_last_admin(target)
        self._users.update_role(user_id, role)

# 02 Add admin service