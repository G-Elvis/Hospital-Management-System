from datetime import date

from app.domain.exceptions import NotFound, PossibleDuplicate
from app.domain.patient import Patient
from app.repositories.base import PatientRepository
from app.validators.patient_validator import PatientValidator, normalise_phone


class PatientService:
    """Orchestrates the patient workflows; the rules live in the validator."""

    def __init__(self, repo: PatientRepository, validator: PatientValidator):
        self._repo = repo
        self._validator = validator

    def register(self, full_name: str, date_of_birth: date | None, gender: str, phone: str,
                 address: str = "", confirm_duplicate: bool = False) -> Patient:
        self._validator.validate(full_name, date_of_birth, phone, gender)
        phone = normalise_phone(phone)
        if not confirm_duplicate and self._repo.find_duplicate(phone, date_of_birth):
            raise PossibleDuplicate(
                "A patient with this phone number and date of birth already exists.")
        patient = Patient(None, full_name.strip(), date_of_birth, gender, phone,
                          (address or "").strip())
        return self._repo.add(patient)

    def get(self, patient_id: int) -> Patient:
        patient = self._repo.get(patient_id)
        if patient is None or not patient.active:
            raise NotFound("Patient not found.")
        return patient

    def search(self, query: str = "") -> list[Patient]:
        return self._repo.search(query or "")

    def list_active(self) -> list[Patient]:
        return self._repo.search("")

    def update_contact(self, patient_id: int, phone: str, address: str) -> Patient:
        patient = self.get(patient_id)
        self._validator.validate(patient.full_name, patient.date_of_birth, phone, patient.gender)
        patient.phone = normalise_phone(phone)
        patient.address = (address or "").strip()
        return self._repo.update(patient)

    def deactivate(self, patient_id: int) -> None:
        self.get(patient_id)                       # raises NotFound if missing
        self._repo.set_active(patient_id, False)   # soft delete: history is kept (FR-PAT-08)
