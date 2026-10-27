from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from app.domain.exceptions import NotFound
from app.domain.medical_record import MedicalRecord
from app.repositories.base import PatientReader, RecordRepository, UserReader
from app.validators.record_validator import RecordValidator


@dataclass(frozen=True)
class RecordEntry:
    record: MedicalRecord
    doctor_name: str


class RecordService:
    """Author and timestamp come from the SERVER (session + clock), never the form."""

    def __init__(self, records: RecordRepository, patients: PatientReader, users: UserReader,
                 validator: RecordValidator, clock: Callable[[], datetime] = datetime.now):
        self._records = records
        self._patients = patients
        self._users = users
        self._validator = validator
        self._clock = clock

    def _require_patient(self, patient_id: int):
        patient = self._patients.get(patient_id)
        if patient is None or not patient.active:
            raise NotFound("Patient not found.")
        return patient

    def add_record(self, doctor_id: int, patient_id: int, diagnosis: str,
                   treatment: str = "", prescription: str = "") -> MedicalRecord:
        self._require_patient(patient_id)
        self._validator.validate(diagnosis, treatment, prescription)
        record = MedicalRecord(None, patient_id, doctor_id, self._clock(), diagnosis.strip(),
                               (treatment or "").strip(), (prescription or "").strip())
        return self._records.add(record)

    def history_for(self, patient_id: int) -> list[RecordEntry]:
        self._require_patient(patient_id)
        entries = []
        for record in self._records.list_for_patient(patient_id):
            doctor = self._users.get(record.doctor_id)
            entries.append(RecordEntry(record, doctor.username if doctor else "Unknown"))
        return entries
