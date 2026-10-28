from datetime import date, datetime, timedelta

import pytest

from app import create_app
from app.domain.user import Role

PASSWORD = "Password123"


@pytest.fixture
def app():
    """A fresh app with its own in-memory database for EVERY test"""
    return create_app({"DATABASE": ":memory:", "TESTING": True,
                       "CSRF_ENABLED": False, "SECRET_KEY": "test"})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    cache = {}

    def _make(username, role):
        if username not in cache:
            cache[username] = app.extensions["admin_service"].create_user(
                username, PASSWORD, Role(role))
        return cache[username]
    return _make


@pytest.fixture
def login_as(client, make_user):
    def _login(role):
        user = make_user(f"{role.lower()}_user", role)
        with client.session_transaction() as sess:
            sess["user_id"] = user.id
        return user
    return _login


@pytest.fixture
def doctor(make_user):
    return make_user("dr_test", "DOCTOR")


@pytest.fixture
def patient(app):
    return app.extensions["patient_service"].register(
        "Jane Doe", date(1990, 5, 1), "Female", "0712345678")


@pytest.fixture
def future_slot():
    def _slot(days_ahead=7, hour=10):
        d = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        d += timedelta(days=days_ahead)
        while d.weekday() == 6:
            d += timedelta(days=1)
        return d
    return _slot


def booking_form(patient_id, doctor_id, when):
    return {"patient_id": patient_id, "doctor_id": doctor_id,
            "date": when.date().isoformat(), "slot": when.strftime("%H:%M")}
