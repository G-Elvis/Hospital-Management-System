from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    RECEPTIONIST = "RECEPTIONIST"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


@dataclass
class User:
    id: int | None
    username: str
    password_hash: str
    role: Role
    active: bool = True
