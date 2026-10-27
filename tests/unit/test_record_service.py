from datetime import date, datetime
from unittest.mock import Mock

import pytest

from app.domain.exceptions import NotFound, ValidationError
from app.domain.medical_record import MedicalRecord
from app.domain.patient import Patient
from app.domain.user import Role, User
from app.repositories.base import PatientReader, RecordRepository, UserReader
from app.services.record_service import RecordService
from app.validators.record_validator import RecordValidator

FIXED_NOW = datetime(2026, 10, 7, 9, 30)


@pytest.fixture
def parts():
    records = Mock(spec=RecordRepository)
    records.add.side_effect = lambda r: r
    patients = Mock(spec=PatientReader)
    patients.get.return_value = Patient(1, "Jane", date(1990, 5, 1), "Female", "0712345678")
    users = Mock(spec=UserReader)
    users.get.return_value = User(7, "dr_ann", "h", Role.DOCTOR)
    service = RecordService(records, patients, users, RecordValidator(), clock=lambda: FIXED_NOW)
    return service, records, patients


def test_author_and_time_are_set_by_the_server(parts):
    service, _, _ = parts
    record = service.add_record(doctor_id=7, patient_id=1, diagnosis="  Malaria ")
    assert record.doctor_id == 7
    assert record.created_at == FIXED_NOW
    assert record.diagnosis == "Malaria"


def test_empty_diagnosis_is_not_saved(parts):
    service, records, _ = parts
    with pytest.raises(ValidationError):
        service.add_record(7, 1, "   ")
    records.add.assert_not_called()


def test_overlong_text_is_rejected(parts):
    service, records, _ = parts
    with pytest.raises(ValidationError):
        service.add_record(7, 1, "x" * 5001)
    records.add.assert_not_called()


def test_unknown_patient_is_rejected(parts):
    service, records, patients = parts
    patients.get.return_value = None
    with pytest.raises(NotFound):
        service.add_record(7, 99, "Flu")
    records.add.assert_not_called()


def test_history_includes_doctor_name(parts):
    service, records, _ = parts
    records.list_for_patient.return_value = [
        MedicalRecord(1, 1, 7, FIXED_NOW, "Flu")]
    entries = service.history_for(1)
    assert entries[0].doctor_name == "dr_ann"


def test_record_writer_interface_has_no_edit_or_delete():
    from app.repositories.base import RecordWriter
    public = {name for name in dir(RecordWriter) if not name.startswith("_")}
    assert public == {"add"}                      # append-only by design (FR-MED-05)
