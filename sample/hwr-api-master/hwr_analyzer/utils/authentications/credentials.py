from enum import Enum


class CredentialsType(Enum):
    SERVICE_CREDENTIALS = 'service_credentials'
    USER_CREDENTIALS = 'user_credentials'


class Credentials:
    def __init__(
        self,
        username: str,
        credential_type: CredentialsType,
        is_active: bool,
    ):
        self.username = username
        self.is_active = is_active
        self.type = credential_type

    def __str__(self):
        return "Credentials"  # pragma: no cover

    def __eq__(self, other):
        return isinstance(other, self.__class__)  # pragma: no cover

    def __hash__(self):
        return 1  # pragma: no cover

    @property
    def is_anonymous(self):
        return False  # pragma: no cover

    @property
    def is_authenticated(self):
        return True

    @property
    def is_service_credentials(self):
        return self.type == CredentialsType.SERVICE_CREDENTIALS
