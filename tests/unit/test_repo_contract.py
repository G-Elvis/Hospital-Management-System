
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from app.domain.appointment import Appointment, AppointmentStatus
from app.domain.exceptions import SlotUnavailable
from app.repositories.memory_appointment_repo import InMemoryAppointmentRepo
from app.repositories.appointment_repo import SqliteAppointmentRepo


def make_sqlite_repo():
    conn = sqlite3.connect(":memory:")
    conn.executescript((Path("app") / "schema.sql").read_text())   # FK checks stay off here
    return SqliteAppointmentRepo(conn)


@pytest.fixture(params=[InMemoryAppointmentRepo, make_sqlite_repo])
def repo(request):
    return request.param()


T = datetime(2030, 1, 8, 10, 0)


def test_add_assigns_an_id(repo):
    assert repo.add(Appointment(None, 1, 2, T)).id is not None


def test_detects_conflict_after_add(repo):
    repo.add(Appointment(None, 1, 2, T))
    assert repo.doctor_has_conflict(2, T) is True


def test_no_conflict_for_other_doctor_or_time(repo):
    repo.add(Appointment(None, 1, 2, T))
    assert repo.doctor_has_conflict(3, T) is False
    assert repo.doctor_has_conflict(2, T + timedelta(minutes=30)) is False


def test_cancelled_appointment_frees_the_slot(repo):
    appointment = repo.add(Appointment(None, 1, 2, T))
    repo.update_status(appointment.id, AppointmentStatus.CANCELLED)
    assert repo.doctor_has_conflict(2, T) is False


def test_doctor_day_list_is_ordered_and_filtered(repo):
    repo.add(Appointment(None, 1, 2, T + timedelta(hours=2)))
    repo.add(Appointment(None, 1, 2, T))
    repo.add(Appointment(None, 1, 3, T))                          # other doctor
    repo.add(Appointment(None, 1, 2, T + timedelta(days=1)))      # other day
    times = [a.start_time for a in repo.list_for_doctor_on_date(2, T.date())]
    assert times == [T, T + timedelta(hours=2)]


def test_get_returns_none_for_unknown_id(repo):
    assert repo.get(12345) is None


def test_sqlite_unique_index_stops_a_race():
    """the database refuses a double booking."""
    repo = make_sqlite_repo()
    repo.add(Appointment(None, 1, 2, T))
    with pytest.raises(SlotUnavailable):
        repo.add(Appointment(None, 5, 2, T))
