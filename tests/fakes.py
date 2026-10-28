from app.security.password_hasher import PasswordHasher


class FastTestHasher(PasswordHasher):
    

    def hash(self, password):
        return f"test${password}"

    def verify(self, password, hashed):
        return hashed == f"test${password}"
