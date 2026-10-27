import sqlite3
from datetime import datetime

from app.domain.appointment import Appointment, AppointmentStatus
from app.domain.exceptions import SlotUnavailable
from app.repositories.base import AppointmentRepository

COLS = "id, patient_id, doctor_id, start_time, status"


def _to_appointment(row) -> Appointment:
    return Appointment(id=row[0], patient_id=row[1], doctor_id=row[2],
                       start_time=datetime.fromisoformat(row[3]),
                       status=AppointmentStatus(row[4]))


class SqliteAppointmentRepo(AppointmentRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def _many(self, sql, params=()):
        return [_to_appointment(r) for r in self._conn.execute(sql, params).fetchall()]

    def get(self, appointment_id):
        row = self._conn.execute(
            f"SELECT {COLS} FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
        return _to_appointment(row) if row else None

    def doctor_has_conflict(self, doctor_id, start_time):
        row = self._conn.execute(
            "SELECT 1 FROM appointments WHERE doctor_id = ? AND start_time = ? "
            "AND status = 'Scheduled'", (doctor_id, start_time.isoformat())).fetchone()
        return row is not None

    def list_all(self):
        return self._many(f"SELECT {COLS} FROM appointments ORDER BY start_time LIMIT 200")

    def list_for_patient(self, patient_id):
        return self._many(f"SELECT {COLS} FROM appointments WHERE patient_id = ? "
                          "ORDER BY start_time DESC", (patient_id,))

    def list_for_doctor_on_date(self, doctor_id, day):
        return self._many(f"SELECT {COLS} FROM appointments WHERE doctor_id = ? "
                          "AND substr(start_time, 1, 10) = ? ORDER BY start_time",
                          (doctor_id, day.isoformat()))

    def add(self, appointment):
        try:
            cur = self._conn.execute(
                "INSERT INTO appointments (patient_id, doctor_id, start_time, status) "
                "VALUES (?, ?, ?, ?)",
                (appointment.patient_id, appointment.doctor_id,
                 appointment.start_time.isoformat(), appointment.status.value))
        except sqlite3.IntegrityError as err:
            if "UNIQUE" in str(err):          # the unique-slot index caught a race
                raise SlotUnavailable("The doctor is already booked at that time.") from err
            raise
        self._conn.commit()
        appointment.id = cur.lastrowid
        return appointment

    def update_status(self, appointment_id, status):
        self._conn.execute("UPDATE appointments SET status = ? WHERE id = ?",
                           (status.value, appointment_id))
        self._conn.commit()

