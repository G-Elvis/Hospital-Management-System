
from abc import ABC, abstractmethod
from datetime import date, datetime

from app.domain.appointment import Appointment, AppointmentStatus
from app.domain.medical_record import MedicalRecord
from app.domain.patient import Patient
from app.domain.user import Role, User


# ---- users -----------------------------------------------------------------
class UserReader(ABC):
    @abstractmethod
    def get(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def list_all(self) -> list[User]: ...

    @abstractmethod
    def list_by_role(self, role: Role) -> list[User]:
        """Active users with this role."""

    @abstractmethod
    def count_active_admins(self) -> int: ...


class UserWriter(ABC):
    @abstractmethod
    def add(self, user: User) -> User: ...

    @abstractmethod
    def update_role(self, user_id: int, role: Role) -> None: ...

    @abstractmethod
    def set_active(self, user_id: int, active: bool) -> None: ...


class UserRepository(UserReader, UserWriter):
    """For classes that need both sides."""


# ---- patients --------------------------------------------------------------
class PatientReader(ABC):
    @abstractmethod
    def get(self, patient_id: int) -> Patient | None: ...

    @abstractmethod
    def search(self, query: str) -> list[Patient]:
        """Active patients matching name / phone / id. Empty query lists the first 50."""

    @abstractmethod
    def find_duplicate(self, phone: str, date_of_birth: date) -> Patient | None: ...


class PatientWriter(ABC):
    @abstractmethod
    def add(self, patient: Patient) -> Patient: ...

    @abstractmethod
    def update(self, patient: Patient) -> Patient: ...

    @abstractmethod
    def set_active(self, patient_id: int, active: bool) -> None: ...


class PatientRepository(PatientReader, PatientWriter):
    pass


# ---- appointments ----------------------------------------------------------
class AppointmentReader(ABC):
    @abstractmethod
    def get(self, appointment_id: int) -> Appointment | None: ...

    @abstractmethod
    def doctor_has_conflict(self, doctor_id: int, start_time: datetime) -> bool: ...

    @abstractmethod
    def list_all(self) -> list[Appointment]: ...

    @abstractmethod
    def list_for_patient(self, patient_id: int) -> list[Appointment]: ...

    @abstractmethod
    def list_for_doctor_on_date(self, doctor_id: int, day: date) -> list[Appointment]: ...


class AppointmentWriter(ABC):
    @abstractmethod
    def add(self, appointment: Appointment) -> Appointment: ...

    @abstractmethod
    def update_status(self, appointment_id: int, status: AppointmentStatus) -> None: ...


class AppointmentRepository(AppointmentReader, AppointmentWriter):
    pass


# ---- medical records -------------------------------------------------------
class RecordReader(ABC):
    @abstractmethod
    def list_for_patient(self, patient_id: int) -> list[MedicalRecord]:
        """Newest first."""


class RecordWriter(ABC):
    @abstractmethod
    def add(self, record: MedicalRecord) -> MedicalRecord: ...


class RecordRepository(RecordReader, RecordWriter):
    pass
