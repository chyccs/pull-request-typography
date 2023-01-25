from unittest.mock import (
    MagicMock,
    patch,
)

import jwt
from django.test import (
    TestCase,
    override_settings,
)
from parameterized import parameterized

from utils.authentications.credentials import CredentialsType
from utils.authentications.simple_authentication import SimpleAuthentication
from utils.testcases.assertion import AssertionMixin


class TestSimpleAuthentication(AssertionMixin, TestCase):
    @staticmethod
    def _create_access_token(user_id: str, token_type: str) -> str:
        return jwt.encode(
            headers={'alg': 'HS256'},
            payload={'sub': user_id, 'type': token_type},
            key='',
        )

    def _create_request(self, user_id: str, token_type: str):
        return MagicMock(
            headers={
                'Authorization': f'Bearer {self._create_access_token(user_id, token_type)}',
            },
        )

    @parameterized.expand([
        ('user_credentials', CredentialsType.USER_CREDENTIALS),
        ('client_credentials', CredentialsType.SERVICE_CREDENTIALS),
    ])
    def test_success_with_credentials(self, type_payload, credentials_type):

        with patch('domain.ndp.services.ndp_requester.requests.post', return_value=MagicMock(active=True)):
            credentials, _ = SimpleAuthentication().authenticate(self._create_request(type_payload, type_payload))

            self.assertEqual(credentials.username, type_payload)
            self.assertEqual(credentials.type, credentials_type)

    @parameterized.expand([
        ('User', 'test_user', CredentialsType.USER_CREDENTIALS),
        ('Client', 'test_client', CredentialsType.SERVICE_CREDENTIALS),
    ])
    @override_settings(ALLOWED_SKIP_AUTHENTICATION=True)
    def test_success_with_header_params(self, key, val, credentials_type):
        request = MagicMock(
            headers={
                key: val,
            },
        )

        credentials, _ = SimpleAuthentication().authenticate(request)

        self.assertEqual(credentials.username, val)
        self.assertEqual(credentials.type, credentials_type)

    @parameterized.expand([
        ('User', 'test_user', CredentialsType.USER_CREDENTIALS),
        ('Client', 'test_client', CredentialsType.SERVICE_CREDENTIALS),
    ])
    @override_settings(ALLOWED_SKIP_AUTHENTICATION=False)
    def test_failure_with_header_params_without_config(self, key, val, _):
        request = MagicMock(
            headers={
                key: val,
            },
        )

        credentials, _ = SimpleAuthentication().authenticate(request)

        self.assertEqual(credentials, None)

    @parameterized.expand([('user_credentials', ), ('client_credentials', )])
    def test_failure_when_header_param_key_is_invalid(self, type_payload):
        request = self._create_request(type_payload, type_payload)
        request.headers['Authorizations'] = request.headers['Authorization']
        request.headers.pop('Authorization')

        credentials, _ = SimpleAuthentication().authenticate(request)

        self.assertEqual(credentials, None)

    @parameterized.expand([('user_credentials', ), ('client_credentials', )])
    def test_failure_when_header_param_value_is_invalid(self, type_payload):
        request = self._create_request(type_payload, type_payload)
        authorization = request.headers['Authorization']
        request.headers['Authorization'] = authorization.replace('Bearer ', 'Bad')

        credentials, _ = SimpleAuthentication().authenticate(request)

        self.assertEqual(credentials, None)
