from datetime import datetime

import pytest

from app.domain.appointment import Appointment, AppointmentStatus

S, C, D = AppointmentStatus.SCHEDULED, AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED


@pytest.mark.parametrize("current, new, allowed", [
    (S, C, True), (S, D, True),
    (C, S, False), (C, D, False),
    (D, C, False), (D, S, False),
])
def test_status_transitions(current, new, allowed):
    appointment = Appointment(1, 1, 2, datetime(2030, 1, 1, 10), current)
    assert appointment.can_become(new) is allowed
