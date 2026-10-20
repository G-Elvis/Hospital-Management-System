


class DomainError(Exception):
    pass


class ValidationError(DomainError):
    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__(" ".join(self.errors))


class PossibleDuplicate(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class NotFound(DomainError):
    pass


class AccessDenied(DomainError):
    pass


class SlotUnavailable(DomainError):
    pass


class InvalidAppointmentTime(DomainError):
    pass


class InvalidStatusChange(DomainError):
    pass
