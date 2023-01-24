import random

from django.shortcuts import resolve_url
from rest_framework.test import APITestCase

from utils.authentications.credentials import (
    Credentials,
    CredentialsType,
)
from utils.test_factories.task import RecognitionTaskFactory
from utils.testcases.assertion import AssertionMixin


# skipcq: PTC-W0046
class TestBase(APITestCase, AssertionMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.task = RecognitionTaskFactory.create(requested_by='test')
        cls.path = resolve_url('recognition_task', task_id=cls.task.task_id)


class TestResponse(TestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(Credentials(username='test',
                                                   credential_type=CredentialsType.USER_CREDENTIALS,
                                                   is_active=True))

    def test_response(self):
        res = self.client.get(self.path)

        self.assertOK(res)


class TestPermission(TestBase):
    def test_permission(self):
        res = self.client.get(self.path)

        self.assertForbidden(res)


class TestParameters(TestBase):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(Credentials(username='test',
                                                   credential_type=CredentialsType.USER_CREDENTIALS,
                                                   is_active=True))

    def test_not_found(self):
        res = self.client.get(resolve_url('recognition_task', task_id=random.randbytes(12).hex()))

        self.assertNotFound(res)

    def test_task_id_is_invalid(self):
        res = self.client.get(resolve_url('recognition_task', task_id='wrong_id'))

        self.assertInvalidParam(res)
