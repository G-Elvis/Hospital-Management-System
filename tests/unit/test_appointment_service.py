from datetime import datetime
from unittest.mock import Mock

import pytest

from app.domain.appointment import Appointment, AppointmentStatus
from app.domain.exceptions import AccessDenied, InvalidStatusChange, NotFound, SlotUnavailable
from app.repositories.base import AppointmentRepository, PatientReader, UserReader
from app.repositories.memory_appointment_repo import InMemoryAppointmentRepo
from app.services.appointment_service import AppointmentService
from app.services.booking_rules import BookingRule

WHEN = datetime(2026, 10, 5, 10, 0)


def make_service(repo=None, rules=()):
    return AppointmentService(repo or InMemoryAppointmentRepo(), list(rules),
                              Mock(spec=PatientReader), Mock(spec=UserReader))


def test_books_as_scheduled_when_all_rules_pass():
    appointment = make_service().book(1, 2, WHEN)          # fake repo: real behaviour, no I/O
    assert appointment.id is not None
    assert appointment.status == AppointmentStatus.SCHEDULED


def test_every_rule_runs_in_order():
    first, second = Mock(spec=BookingRule), Mock(spec=BookingRule)
    order = Mock()
    order.attach_mock(first.check, "first")
    order.attach_mock(second.check, "second")
    make_service(rules=[first, second]).book(1, 2, WHEN)
    assert [c[0] for c in order.mock_calls] == ["first", "second"]


def test_failing_rule_blocks_saving():
    failing = Mock(spec=BookingRule)
    failing.check.side_effect = SlotUnavailable("taken")
    repo = Mock(spec=AppointmentRepository)
    with pytest.raises(SlotUnavailable):
        make_service(repo, [failing]).book(1, 2, WHEN)
    repo.add.assert_not_called()


def test_cancel_scheduled_appointment():
    repo = InMemoryAppointmentRepo()
    service = make_service(repo)
    appointment = service.book(1, 2, WHEN)
    service.cancel(appointment.id)
    assert repo.get(appointment.id).status == AppointmentStatus.CANCELLED


def test_cancelled_slot_frees_the_doctor():
    repo = InMemoryAppointmentRepo()
    service = make_service(repo)
    appointment = service.book(1, 2, WHEN)
    assert repo.doctor_has_conflict(2, WHEN)
    service.cancel(appointment.id)
    assert not repo.doctor_has_conflict(2, WHEN)


def test_completed_appointment_cannot_be_cancelled():
    service = make_service()
    appointment = service.book(1, 2, WHEN)
    service.mark_completed(appointment.id, doctor_id=2)
    with pytest.raises(InvalidStatusChange):
        service.cancel(appointment.id)


def test_cancelling_twice_is_rejected():
    service = make_service()
    appointment = service.book(1, 2, WHEN)
    service.cancel(appointment.id)
    with pytest.raises(InvalidStatusChange):
        service.cancel(appointment.id)


def test_unknown_appointment_is_not_found():
    with pytest.raises(NotFound):
        make_service().cancel(999)


def test_doctor_cannot_complete_another_doctors_appointment():
    service = make_service()
    appointment = service.book(1, 2, WHEN)
    with pytest.raises(AccessDenied):
        service.mark_completed(appointment.id, doctor_id=3)


def test_booked_times_ignores_cancelled():
    repo = InMemoryAppointmentRepo()
    service = make_service(repo)
    keep = service.book(1, 2, WHEN)
    gone = service.book(1, 2, datetime(2026, 10, 5, 11, 0))
    service.cancel(gone.id)
    assert service.booked_times(2, WHEN.date()) == {WHEN.time()}
    assert keep.id != gone.id
