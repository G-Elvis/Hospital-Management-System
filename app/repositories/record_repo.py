import sqlite3
from datetime import date

from app.domain.patient import Patient
from app.repositories.base import PatientRepository

COLS = "id, full_name, date_of_birth, gender, phone, address, active"


def _to_patient(row) -> Patient:
    return Patient(id=row[0], full_name=row[1], date_of_birth=date.fromisoformat(row[2]),
                   gender=row[3], phone=row[4], address=row[5], active=bool(row[6]))


def _escape_like(text: str) -> str:
    """Make % and _ typed by the user match literally instead of acting as wildcards."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class SqlitePatientRepo(PatientRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get(self, patient_id):
        row = self._conn.execute(
            f"SELECT {COLS} FROM patients WHERE id = ?", (patient_id,)).fetchone()
        return _to_patient(row) if row else None

    def search(self, query):
        q = query.strip()
        if not q:
            sql, params = (f"SELECT {COLS} FROM patients WHERE active = 1 "
                           "ORDER BY full_name LIMIT 50"), ()
        else:
            like = f"%{_escape_like(q)}%"
            sql = (f"SELECT {COLS} FROM patients WHERE active = 1 AND "
                   "(full_name LIKE ? ESCAPE '\\' OR phone LIKE ? ESCAPE '\\' OR id = ?) "
                   "ORDER BY full_name LIMIT 50")
            params = (like, like, int(q) if q.isdigit() else -1)
        return [_to_patient(r) for r in self._conn.execute(sql, params).fetchall()]

    def find_duplicate(self, phone, date_of_birth):
        row = self._conn.execute(
            f"SELECT {COLS} FROM patients WHERE phone = ? AND date_of_birth = ? AND active = 1 "
            "LIMIT 1", (phone, date_of_birth.isoformat())).fetchone()
        return _to_patient(row) if row else None

    def add(self, patient):
        cur = self._conn.execute(
            "INSERT INTO patients (full_name, date_of_birth, gender, phone, address, active) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (patient.full_name, patient.date_of_birth.isoformat(), patient.gender,
             patient.phone, patient.address, int(patient.active)))
        self._conn.commit()
        patient.id = cur.lastrowid
        return patient

    def update(self, patient):
        self._conn.execute(
            "UPDATE patients SET full_name = ?, gender = ?, phone = ?, address = ? WHERE id = ?",
            (patient.full_name, patient.gender, patient.phone, patient.address, patient.id))
        self._conn.commit()
        return patient

    def set_active(self, patient_id, active):
        self._conn.execute("UPDATE patients SET active = ? WHERE id = ?",
                           (int(active), patient_id))
        self._conn.commit()
