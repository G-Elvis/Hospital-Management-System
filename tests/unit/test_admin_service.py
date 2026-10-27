import pytest

from app.domain.exceptions import DomainError, NotFound, ValidationError
from app.domain.user import Role
from app.services.admin_service import AdminService
from tests.fakes import FastTestHasher


class FakeUserRepo:
    """A tiny in-memory UserRepository (duck-typed, enough for these tests)."""

    def __init__(self):
        self.users = {}

    def add(self, user):
        if any(u.username.lower() == user.username.lower() for u in self.users.values()):
            raise DomainError("That username is already taken.")
        user.id = len(self.users) + 1
        self.users[user.id] = user
        return user

    def get(self, user_id):
        return self.users.get(user_id)

    def list_all(self):
        return list(self.users.values())

    def count_active_admins(self):
        return sum(1 for u in self.users.values() if u.role == Role.ADMIN and u.active)

    def update_role(self, user_id, role):
        self.users[user_id].role = role

    def set_active(self, user_id, active):
        self.users[user_id].active = active


@pytest.fixture
def service():
    return AdminService(FakeUserRepo(), FastTestHasher())


def test_create_user_hashes_password(service):
    user = service.create_user("ann", "longenough", "DOCTOR")
    assert user.password_hash != "longenough"
    assert user.role == Role.DOCTOR


@pytest.mark.parametrize("username, password, role", [
    ("", "longenough", "DOCTOR"), ("ann", "short", "DOCTOR"), ("ann", "longenough", "WIZARD"),
])
def test_invalid_account_is_rejected(service, username, password, role):
    with pytest.raises(ValidationError):
        service.create_user(username, password, role)


def test_duplicate_username_is_rejected(service):
    service.create_user("ann", "longenough", "DOCTOR")
    with pytest.raises(DomainError):
        service.create_user("ANN", "longenough", "RECEPTIONIST")


def test_deactivate_user(service):
    user = service.create_user("ann", "longenough", "DOCTOR")
    service.deactivate(user.id)
    assert service.list_users()[0].active is False


def test_cannot_deactivate_or_demote_the_last_admin(service):
    admin = service.create_user("root", "longenough", "ADMIN")
    with pytest.raises(DomainError):
        service.deactivate(admin.id)
    with pytest.raises(DomainError):
        service.change_role(admin.id, "DOCTOR")


def test_can_demote_an_admin_when_another_exists(service):
    first = service.create_user("root", "longenough", "ADMIN")
    service.create_user("root2", "longenough", "ADMIN")
    service.change_role(first.id, "DOCTOR")
    assert first.role == Role.DOCTOR


def test_unknown_user_is_not_found(service):
    with pytest.raises(NotFound):
        service.deactivate(42)
