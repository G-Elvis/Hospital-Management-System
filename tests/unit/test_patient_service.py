from datetime import date
from unittest.mock import Mock

import pytest

from app.domain.exceptions import NotFound, PossibleDuplicate, ValidationError
from app.domain.patient import Patient
from app.repositories.base import PatientRepository
from app.services.patient_service import PatientService
from app.validators.patient_validator import PatientValidator

DOB = date(1990, 5, 1)


@pytest.fixture
def repo():
    r = Mock(spec=PatientRepository)        # spec= rejects calls to methods that don't exist
    r.find_duplicate.return_value = None    # stub: canned answer
    r.add.side_effect = lambda patient: patient
    return r


@pytest.fixture
def service(repo):
    return PatientService(repo, PatientValidator())


def test_register_saves_trimmed_normalised_patient(service, repo):
    result = service.register("  Jane Doe ", DOB, "Female", "0712 345 678")
    repo.add.assert_called_once()           # mock: behaviour check
    assert result.full_name == "Jane Doe"
    assert result.phone == "0712345678"


def test_invalid_input_is_never_saved(service, repo):
    with pytest.raises(ValidationError):
        service.register("", DOB, "Female", "0712345678")
    repo.add.assert_not_called()


def test_duplicate_is_flagged_and_not_saved(service, repo):
    repo.find_duplicate.return_value = Patient(1, "Jane", DOB, "Female", "0712345678")
    with pytest.raises(PossibleDuplicate):
        service.register("Jane Doe", DOB, "Female", "0712345678")
    repo.add.assert_not_called()


def test_duplicate_can_be_confirmed(service, repo):
    repo.find_duplicate.return_value = Patient(1, "Jane", DOB, "Female", "0712345678")
    service.register("Jane Doe", DOB, "Female", "0712345678", confirm_duplicate=True)
    repo.add.assert_called_once()


def test_get_unknown_or_inactive_patient_is_not_found(service, repo):
    repo.get.return_value = None
    with pytest.raises(NotFound):
        service.get(99)
    repo.get.return_value = Patient(1, "Jane", DOB, "Female", "0712345678", active=False)
    with pytest.raises(NotFound):
        service.get(1)


def test_update_contact_validates_new_phone(service, repo):
    repo.get.return_value = Patient(1, "Jane", DOB, "Female", "0712345678")
    with pytest.raises(ValidationError):
        service.update_contact(1, "bad", "Nairobi")
    repo.update.assert_not_called()


def test_deactivate_is_a_soft_delete(service, repo):
    repo.get.return_value = Patient(1, "Jane", DOB, "Female", "0712345678")
    service.deactivate(1)
    repo.set_active.assert_called_once_with(1, False)
