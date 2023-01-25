import json
from unittest.mock import (
    Mock,
    patch,
)

from rest_framework.test import APITestCase

from services.restful.tasks import try_recognize_to_health_check
from utils.authentications.credentials import (
    Credentials,
    CredentialsType,
)
from utils.testcases.assertion import AssertionMixin


def make_recognition_result(label: str):
    return json.dumps(
        [
            {"iink": {"type": "Text", "label": label}},
        ],
        ensure_ascii=False)


@patch('services.restful.views.recognizer.recognize_pages_async.apply_async')
class TestTasks(APITestCase, AssertionMixin):

    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(Credentials(username='test',
                                                   credential_type=CredentialsType.USER_CREDENTIALS,
                                                   is_active=True))

    def patched_post(self, path, data):
        res = self.client.post(path, data=data, **{
            'HTTP_USER': 'health_checker',
            'HTTP_AWAIT': 'true',
        })
        result = Mock()
        result.json.return_value = res.data
        return result

    def test_recognize_success_on_health_check(self, apply_async):
        apply_async.return_value.get.return_value = make_recognition_result('치약')

        with patch('services.restful.tasks.post', self.patched_post):

            try_recognize_to_health_check()

            apply_async.assert_called()

    def test_recognize_failure_on_health_check(self, apply_async):
        apply_async.return_value.get.return_value = make_recognition_result('치솔')

        with patch('services.restful.tasks.post', self.patched_post), self.assertRaises(AssertionError):
            try_recognize_to_health_check()

            apply_async.assert_called()
