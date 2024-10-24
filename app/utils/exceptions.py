class ValidationError(Exception):
    def __init__(self, message) -> None:
        self.message = message


class AuthenticationError(Exception):
    def __init__(self, message="Authentication failed") -> None:
        self.message = message


class AuthorizationError(Exception):
    def __init__(self, message="Authorization failed") -> None:
        self.message = message


class DatabaseError(Exception):
    def __init__(self, message="Database operation failed") -> None:
        self.message = message
