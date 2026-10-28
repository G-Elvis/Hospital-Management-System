from datetime import datetime

from app.domain.appointment import Appointment, AppointmentStatus
from app.repositories.base import AppointmentRepository


class InMemoryAppointmentRepo(AppointmentRepository):
    """A real, working substitute for SqliteAppointmentRepo (Liskov Substitution).

    Used by fast unit tests and proven equivalent by the contract tests.
    """

    def __init__(self):
        self._items: list[Appointment] = []

    def get(self, appointment_id):
        return next((a for a in self._items if a.id == appointment_id), None)

    def doctor_has_conflict(self, doctor_id, start_time: datetime):
        return any(a.doctor_id == doctor_id and a.start_time == start_time
                   and a.status == AppointmentStatus.SCHEDULED for a in self._items)

    def list_all(self):
        return sorted(self._items, key=lambda a: a.start_time)

    def list_for_patient(self, patient_id):
        return sorted((a for a in self._items if a.patient_id == patient_id),
                      key=lambda a: a.start_time, reverse=True)

    def list_for_doctor_on_date(self, doctor_id, day):
        return sorted((a for a in self._items
                       if a.doctor_id == doctor_id and a.start_time.date() == day),
                      key=lambda a: a.start_time)

    def add(self, appointment):
        appointment.id = len(self._items) + 1
        self._items.append(appointment)
        return appointment

    def update_status(self, appointment_id, status):
        self.get(appointment_id).status = status

# 01 Implement memory appointment repo intrerface