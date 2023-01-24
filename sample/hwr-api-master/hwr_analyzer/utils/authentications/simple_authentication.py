import jwt
from channels.auth import AuthMiddlewareStack
from django.conf import settings
from rest_framework.authentication import BaseAuthentication

from domain.ndp.services.ndp_requester import fetch_instrospect_token
from utils.authentications.credentials import (
    Credentials,
    CredentialsType,
)


def _handle_header(headers: dict):
    try:
        if (user := headers.get('User')) and settings.ALLOWED_SKIP_AUTHENTICATION:
            return Credentials(
                username=user,
                is_active=True,
                credential_type=CredentialsType.USER_CREDENTIALS,
            )

        if (client := headers.get('Client')) and settings.ALLOWED_SKIP_AUTHENTICATION:
            return Credentials(
                username=client,
                is_active=True,
                credential_type=CredentialsType.SERVICE_CREDENTIALS,
            )

        token_parts = headers['Authorization'].split(None, 1)
        if len(token_parts) != 2:
            raise RuntimeError()

        token_type, token = token_parts
        if token_type != 'Bearer':
            raise RuntimeError()

        _validate_access_token(token)
        return _decode_payload(token)

    except Exception:  # skipcq: PYL-W0703
        return None


class SimpleAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return _handle_header(headers=request.headers), None


class TokenAuthMiddleware:  # pragma: no cover
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        parsed_header = {
            'Authorization': headers.get(b'Authorization'),
            'User': headers.get(b'User'),
            'Client': headers.get(b'Client'),
        }
        credentials, _ = _handle_header(headers=parsed_header)
        scope['user'] = credentials
        return await self.inner(scope, receive, send)


# pylint: disable=C0103


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))


def _validate_access_token(token):
    res = fetch_instrospect_token(token)
    if not res.json().get('active', False):
        raise RuntimeError('auth failed')


def _decode_payload(encoded) -> Credentials:
    decoded = jwt.decode(encoded, options={"verify_signature": False})
    return Credentials(
        username=decoded['sub'],
        is_active=True,
        credential_type=(CredentialsType.SERVICE_CREDENTIALS
                         if decoded['type'] == "client_credentials" else CredentialsType.USER_CREDENTIALS),
    )
