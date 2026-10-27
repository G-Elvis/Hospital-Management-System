from datetime import datetime
from unittest.mock import Mock

import pytest

from app.domain.exceptions import DomainError, InvalidAppointmentTime, SlotUnavailable
from app.domain.patient import Patient
from app.domain.user import Role, User
from app.repositories.base import AppointmentReader, PatientReader, UserReader
from app.services.booking_rules import (BookingRequest, DoctorExistsRule, NoDoctorConflictRule,
                                        NoSundayRule, NotInPastRule, PatientExistsRule,
                                        ValidSlotRule)

NOW = datetime(2026, 10, 1, 12, 0)          # a fixed Thursday


def request_at(when):
    return BookingRequest(patient_id=1, doctor_id=2, start_time=when)


class TestNotInPastRule:
    rule = NotInPastRule(clock=lambda: NOW)     # injected clock: no dependence on real time

    def test_rejects_past(self):
        with pytest.raises(InvalidAppointmentTime):
            self.rule.check(request_at(datetime(2026, 10, 1, 11, 0)))

    def test_rejects_exactly_now(self):         # boundary value: catches '<' vs '<='
        with pytest.raises(InvalidAppointmentTime):
            self.rule.check(request_at(NOW))

    def test_accepts_future(self):
        self.rule.check(request_at(datetime(2026, 10, 1, 13, 0)))


class TestValidSlotRule:
    @pytest.mark.parametrize("hour, minute", [(9, 0), (12, 30), (16, 30)])
    def test_accepts_clinic_slots(self, hour, minute):
        ValidSlotRule().check(request_at(datetime(2026, 10, 5, hour, minute)))

    @pytest.mark.parametrize("hour, minute", [(8, 30), (17, 0), (10, 15)])
    def test_rejects_other_times(self, hour, minute):
        with pytest.raises(InvalidAppointmentTime):
            ValidSlotRule().check(request_at(datetime(2026, 10, 5, hour, minute)))


class TestNoSundayRule:
    def test_rejects_sunday(self):
        with pytest.raises(InvalidAppointmentTime):
            NoSundayRule().check(request_at(datetime(2026, 10, 4, 10, 0)))

    def test_accepts_monday(self):
        NoSundayRule().check(request_at(datetime(2026, 10, 5, 10, 0)))


class TestNoDoctorConflictRule:
    def test_rejects_when_repo_reports_conflict(self):
        repo = Mock(spec=AppointmentReader)
        repo.doctor_has_conflict.return_value = True
        with pytest.raises(SlotUnavailable):
            NoDoctorConflictRule(repo).check(request_at(NOW))
        repo.doctor_has_conflict.assert_called_once_with(2, NOW)

    def test_accepts_free_slot(self):
        repo = Mock(spec=AppointmentReader)
        repo.doctor_has_conflict.return_value = False
        NoDoctorConflictRule(repo).check(request_at(NOW))


class TestPatientExistsRule:
    def test_rejects_unknown_patient(self):
        patients = Mock(spec=PatientReader)
        patients.get.return_value = None
        with pytest.raises(DomainError):
            PatientExistsRule(patients).check(request_at(NOW))

    def test_rejects_inactive_patient(self):
        patients = Mock(spec=PatientReader)
        patients.get.return_value = Patient(1, "J", NOW.date(), "Female", "0712345678", active=False)
        with pytest.raises(DomainError):
            PatientExistsRule(patients).check(request_at(NOW))


class TestDoctorExistsRule:
    @pytest.mark.parametrize("user", [
        None,
        User(2, "rec", "h", Role.RECEPTIONIST),                  # wrong role
        User(2, "dr", "h", Role.DOCTOR, active=False),           # deactivated
    ])
    def test_rejects_invalid_doctor(self, user):
        users = Mock(spec=UserReader)
        users.get.return_value = user
        with pytest.raises(DomainError):
            DoctorExistsRule(users).check(request_at(NOW))

    def test_accepts_active_doctor(self):
        users = Mock(spec=UserReader)
        users.get.return_value = User(2, "dr", "h", Role.DOCTOR)
        DoctorExistsRule(users).check(request_at(NOW))
