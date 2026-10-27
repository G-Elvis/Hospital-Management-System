from dataclasses import dataclass
from datetime import date, datetime

from app.domain.appointment import Appointment, AppointmentStatus
from app.domain.exceptions import AccessDenied, InvalidStatusChange, NotFound
from app.domain.user import Role
from app.repositories.base import AppointmentRepository, PatientReader, UserReader
from app.services.booking_rules import BookingRequest, BookingRule


@dataclass(frozen=True)
class AppointmentView:
    """An appointment plus display names, so templates stay free of lookups."""

    appointment: Appointment
    patient_name: str
    doctor_name: str


class AppointmentService:
    def __init__(self, repo: AppointmentRepository, rules: list[BookingRule],
                 patients: PatientReader, users: UserReader):
        self._repo = repo
        self._rules = rules
        self._patients = patients
        self._users = users


    def book(self, patient_id: int, doctor_id: int, start_time: datetime) -> Appointment:
        request = BookingRequest(patient_id, doctor_id, start_time)
        for rule in self._rules:                 # closed for modification
            rule.check(request)
        return self._repo.add(Appointment(None, patient_id, doctor_id, start_time))

    def _get(self, appointment_id: int) -> Appointment:
        appointment = self._repo.get(appointment_id)
        if appointment is None:
            raise NotFound("Appointment not found.")
        return appointment

    def cancel(self, appointment_id: int) -> None:
        appointment = self._get(appointment_id)
        if not appointment.can_become(AppointmentStatus.CANCELLED):
            if appointment.status == AppointmentStatus.COMPLETED:
                raise InvalidStatusChange("Completed appointments cannot be cancelled.")
            raise InvalidStatusChange("This appointment is already cancelled.")
        self._repo.update_status(appointment_id, AppointmentStatus.CANCELLED)

    def mark_completed(self, appointment_id: int, doctor_id: int) -> None:
        appointment = self._get(appointment_id)
        if appointment.doctor_id != doctor_id:        # doctors may only touch their own
            raise AccessDenied("This appointment belongs to another doctor.")
        if not appointment.can_become(AppointmentStatus.COMPLETED):
            raise InvalidStatusChange("Only scheduled appointments can be completed.")
        self._repo.update_status(appointment_id, AppointmentStatus.COMPLETED)


    def _views(self, appointments) -> list[AppointmentView]:
        views = []
        for a in appointments:
            patient = self._patients.get(a.patient_id)
            doctor = self._users.get(a.doctor_id)
            views.append(AppointmentView(a, patient.full_name if patient else "Unknown",
                                         doctor.username if doctor else "Unknown"))
        return views

    def list_all(self) -> list[AppointmentView]:
        return self._views(self._repo.list_all())

    def history_for_patient(self, patient_id: int) -> list[AppointmentView]:
        return self._views(self._repo.list_for_patient(patient_id))

    def schedule_for(self, doctor_id: int, day: date) -> list[AppointmentView]:
        return self._views(self._repo.list_for_doctor_on_date(doctor_id, day))

    def booked_times(self, doctor_id: int, day: date) -> set:
        return {a.start_time.time() for a in self._repo.list_for_doctor_on_date(doctor_id, day)
                if a.status == AppointmentStatus.SCHEDULED}

    def list_doctors(self):
        return self._users.list_by_role(Role.DOCTOR)
