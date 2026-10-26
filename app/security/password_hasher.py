from abc import ABC, abstractmethod

from werkzeug.security import check_password_hash, generate_password_hash


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool: ...


class WerkzeugPasswordHasher(PasswordHasher):

    def hash(self, password):
        return generate_password_hash(password)

    def verify(self, password, hashed):
        return check_password_hash(hashed, password)