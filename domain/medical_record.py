from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MedicalRecord:
    id: int | None
    patient_id: int
    doctor_id: int
    created_at: datetime
    diagnosis: str
    treatment: str = ""
    prescription: str = ""
