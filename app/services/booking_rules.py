"""Pluggable booking rules - the Open/Closed Principle in action.

AppointmentService never changes when a policy changes: write a new BookingRule
class and add it to the list in create_app().
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, time
from typing import Callable

from app.domain.exceptions import DomainError, InvalidAppointmentTime, SlotUnavailable
from app.domain.user import Role
from app.repositories.base import AppointmentReader, PatientReader, UserReader

# 09:00 ... 16:30 in 30-minute slots
SLOT_TIMES = [time(h, m) for h in range(9, 17) for m in (0, 30)]


@dataclass(frozen=True)
class BookingRequest:
    patient_id: int
    doctor_id: int
    start_time: datetime


class BookingRule(ABC):
    @abstractmethod
    def check(self, request: BookingRequest) -> None:
        """Raise a DomainError if the request breaks this rule."""


class NotInPastRule(BookingRule):
    def __init__(self, clock: Callable[[], datetime] = datetime.now):
        self._clock = clock                       # injected so tests control time

    def check(self, request):
        if request.start_time <= self._clock():
            raise InvalidAppointmentTime("Appointments must be in the future.")


class ValidSlotRule(BookingRule):
    def check(self, request):
        t = request.start_time
        if t.time() not in SLOT_TIMES:
            raise InvalidAppointmentTime(
                "Choose a 30-minute slot between 09:00 and 16:30.")


class NoSundayRule(BookingRule):
    def check(self, request):
        if request.start_time.weekday() == 6:
            raise InvalidAppointmentTime("The clinic is closed on Sundays.")


class PatientExistsRule(BookingRule):
    def __init__(self, patients: PatientReader):
        self._patients = patients

    def check(self, request):
        patient = self._patients.get(request.patient_id)
        if patient is None or not patient.active:
            raise DomainError("Patient not found.")


class DoctorExistsRule(BookingRule):
    def __init__(self, users: UserReader):
        self._users = users

    def check(self, request):
        doctor = self._users.get(request.doctor_id)
        if doctor is None or not doctor.active or doctor.role != Role.DOCTOR:
            raise DomainError("Select a valid doctor.")


class NoDoctorConflictRule(BookingRule):
    def __init__(self, appointments: AppointmentReader):
        self._appointments = appointments

    def check(self, request):
        if self._appointments.doctor_has_conflict(request.doctor_id, request.start_time):
            raise SlotUnavailable("The doctor is already booked at that time.")
