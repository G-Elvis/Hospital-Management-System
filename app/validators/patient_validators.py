import re
from datetime import date

from app.domain.exceptions import ValidationError

PHONE_PATTERN = re.compile(r"^\+?\d[\d\s]{8,14}$")
GENDERS = ("Female", "Male", "Other")


def normalise_phone(phone: str) -> str:
    return re.sub(r"\s+", "", phone or "")


class PatientValidator:

    def validate(self, full_name, date_of_birth, phone, gender="Other"):
        errors = []
        if not full_name or not full_name.strip():
            errors.append("Full name is required.")
        if date_of_birth is None or date_of_birth > date.today():
            errors.append("Date of birth must be a valid date in the past.")
        if not phone or not PHONE_PATTERN.match(phone.strip()):
            errors.append("Enter a valid phone number.")
        if gender not in GENDERS:
            errors.append("Select a gender.")
        if errors:
            raise ValidationError(errors)   # report ALL problems at once
