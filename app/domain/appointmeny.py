from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

ALLOWED_TRANSITIONS = {
    AppointmentStatus.SCHEDULED: {AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED},
    AppointmentStatus.CANCELLED: set(),
    AppointmentStatus.COMPLETED: set(),
}

@dataclass
class Appointment:
    id: int | None
    patient_id: int
    doctor_id: int
    start_time: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED

    def can_become(self, new_status: AppointmentStatus) -> bool:
        return new_status in ALLOWED_TRANSITIONS[self.status]
