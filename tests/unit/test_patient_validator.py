from datetime import date, timedelta

import pytest

from app.domain.exceptions import ValidationError
from app.validators.patient_validator import PatientValidator, normalise_phone

validator = PatientValidator()
GOOD_DOB = date(1990, 5, 1)


def test_valid_input_passes():
    validator.validate("Jane Doe", GOOD_DOB, "0712 345 678", "Female")


@pytest.mark.parametrize("name, dob, phone, gender, expected", [
    ("", GOOD_DOB, "0712345678", "Female", "Full name is required."),
    ("   ", GOOD_DOB, "0712345678", "Female", "Full name is required."),
    ("Jane", date.today() + timedelta(days=1), "0712345678", "Female",
     "Date of birth must be a valid date in the past."),
    ("Jane", None, "0712345678", "Female", "Date of birth must be a valid date in the past."),
    ("Jane", GOOD_DOB, "abc", "Female", "Enter a valid phone number."),
    ("Jane", GOOD_DOB, "", "Female", "Enter a valid phone number."),
    ("Jane", GOOD_DOB, "0712345678", "", "Select a gender."),
])
def test_rejects_invalid_field(name, dob, phone, gender, expected):
    with pytest.raises(ValidationError) as exc:
        validator.validate(name, dob, phone, gender)
    assert expected in exc.value.errors


def test_reports_all_errors_at_once():
    with pytest.raises(ValidationError) as exc:
        validator.validate("", None, "x", "")
    assert len(exc.value.errors) == 4


def test_phone_spaces_are_normalised():
    assert normalise_phone("0712 345 678") == "0712345678"
