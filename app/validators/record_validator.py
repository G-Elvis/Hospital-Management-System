from app.domain.exceptions import ValidationError

MAX_LENGTH = 5000


class RecordValidator:

    def validate(self, diagnosis, treatment="", prescription=""):
        errors = []
        if not diagnosis or not diagnosis.strip():
            errors.append("Diagnosis is required.")
        for label, text in (("Diagnosis", diagnosis), ("Treatment notes", treatment),
                            ("Prescription notes", prescription)):
            if text and len(text) > MAX_LENGTH:
                errors.append(f"{label} must be at most {MAX_LENGTH} characters.")
        if errors:
            raise ValidationError(errors)
