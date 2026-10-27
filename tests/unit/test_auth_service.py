from unittest.mock import Mock

import pytest

from app.domain.exceptions import AuthenticationError
from app.domain.user import Role, User
from app.repositories.base import UserReader
from app.security.password_hasher import WerkzeugPasswordHasher
from app.services.auth_service import AuthService
from tests.fakes import FastTestHasher

hasher = FastTestHasher()


def make_service(user):
    repo = Mock(spec=UserReader)
    repo.get_by_username.return_value = user
    return AuthService(repo, hasher)


def doctor(**overrides):
    fields = dict(id=1, username="ann", password_hash=hasher.hash("secret"),
                  role=Role.DOCTOR, active=True)
    fields.update(overrides)
    return User(**fields)


def test_correct_credentials_return_user():
    user = doctor()
    assert make_service(user).login("ann", "secret") is user


@pytest.mark.parametrize("user, password", [
    (doctor(), "wrong-password"),
    (None, "secret"),
    (doctor(active=False), "secret"),
])
def test_all_failures_give_the_same_generic_message(user, password):
    with pytest.raises(AuthenticationError) as exc:
        make_service(user).login("ann", password)
    assert str(exc.value) == "Invalid username or password."


def test_real_hasher_never_stores_plain_text_and_salts():
    real = WerkzeugPasswordHasher()
    first, second = real.hash("secret123"), real.hash("secret123")
    assert first != "secret123"
    assert first != second                       # salted: same password, different hash
    assert real.verify("secret123", first)
    assert not real.verify("wrong", first)
