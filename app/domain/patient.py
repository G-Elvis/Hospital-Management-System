from dataclasses import dataclass
from datetime import date


@dataclass
class Patient:
    id: int | None
    full_name: str
    date_of_birth: date
    gender: str
    phone: str
    address: str = ""
    active: bool = True
