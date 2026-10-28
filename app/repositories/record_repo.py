import sqlite3
from datetime import datetime
from dataclasses import replace

from app.domain.medical_record import MedicalRecord
from app.repositories.base import RecordRepository

COLS = "id, patient_id, doctor_id, created_at, diagnosis, treatment, prescription"


def _to_record(row) -> MedicalRecord:
    return MedicalRecord(id=row[0], patient_id=row[1], doctor_id=row[2],
                         created_at=datetime.fromisoformat(row[3]), diagnosis=row[4],
                         treatment=row[5], prescription=row[6])


class SqliteRecordRepo(RecordRepository):
    """Append-only: there is deliberately no update or delete method."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add(self, record):
        cur = self._conn.execute(
            "INSERT INTO medical_records (patient_id, doctor_id, created_at, diagnosis, "
            "treatment, prescription) VALUES (?, ?, ?, ?, ?, ?)",
            (record.patient_id, record.doctor_id, record.created_at.isoformat(),
             record.diagnosis, record.treatment, record.prescription))
        self._conn.commit()
        return replace(record, id=cur.lastrowid)

    def list_for_patient(self, patient_id):
        rows = self._conn.execute(
            f"SELECT {COLS} FROM medical_records WHERE patient_id = ? "
            "ORDER BY created_at DESC, id DESC", (patient_id,)).fetchall()
        return [_to_record(r) for r in rows]