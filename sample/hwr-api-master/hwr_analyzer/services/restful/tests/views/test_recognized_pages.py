from unittest.mock import (
    MagicMock,
    patch,
)

from django.shortcuts import resolve_url
from rest_framework.test import APITestCase

from utils.authentications.credentials import (
    Credentials,
    CredentialsType,
)
from utils.testcases.assertion import AssertionMixin


# skipcq: PTC-W0046
class TestBase(APITestCase, AssertionMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = resolve_url('recognized_pages')


@patch('services.restful.views.recognized_pages.BaseRecognizedPagesView._find_recognized_document')
class TestResponse(TestBase):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(Credentials(username='test',
                                                   credential_type=CredentialsType.USER_CREDENTIALS,
                                                   is_active=True))

    def test_response(self, find):
        find.return_value = [MagicMock()]

        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertOK(res)
        contents = res.data['contents']
        self.assertEqual(len(contents), 1)

    def test_response_not_found(self, find):
        find.return_value = []

        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertOK(res)
        contents = res.data['contents']
        self.assertEqual(len(contents), 0)

    def test_response_with_side_effect(self, find):
        find.side_effect = RuntimeError

        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertInternalServer(res)


@patch('services.restful.views.recognized_pages.BaseRecognizedPagesView._find_recognized_document')
@patch('domain.ndp.services.ndp_requester.requests.get')
class TestResponseUserRecognizedPages(TestBase):
    def setUp(self) -> None:
        super().setUp()
        self.path = resolve_url('user_recognized_pages', user_id='test')
        self.client.force_authenticate(Credentials(username='admin',
                                                   credential_type=CredentialsType.SERVICE_CREDENTIALS,
                                                   is_active=True))

    @staticmethod
    def create_result_of_fetching_users(has_perm: bool):
        return [
            {
                'id': 'test',
                'originId': '',
                'name': 'tester',
                'email': 'test@test',
                'birthday': '2022-01-01',
                'gender': 'Male',
                'nationality': 'Korea',
                'pictureUrl': '',
                'visitCount': 1,
                'allowedPushMessage': True,
                'canShare': True,
                'extra': '',
            },
        ] if has_perm else []

    def test_has_no_permission_to_access_user(self, fetch_entire_users, _):
        fetch_entire_users.return_value.json.return_value = self.create_result_of_fetching_users(has_perm=False)

        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertForbidden(res)

    def test_response(self, fetch_entire_users, find):
        find.return_value = [MagicMock()]
        fetch_entire_users.return_value.json.return_value = self.create_result_of_fetching_users(has_perm=True)

        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertOK(res)
        contents = res.data['contents']
        self.assertEqual(len(contents), 1)

    def test_response_user_recognized_pages_not_found(self, fetch_entire_users, find):
        find.return_value = []
        fetch_entire_users.return_value.json.return_value = self.create_result_of_fetching_users(has_perm=True)

        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertOK(res)
        contents = res.data['contents']
        self.assertEqual(len(contents), 0)

    def test_response_with_side_effect(self, fetch_entire_users, find):
        find.side_effect = RuntimeError
        fetch_entire_users.return_value.json.return_value = self.create_result_of_fetching_users(has_perm=True)

        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertInternalServer(res)


class TestPermission(TestBase):
    def test_permission(self):
        res = self.client.get(self.path, data={'keyword': 'keyword'})

        self.assertForbidden(res)

    def test_permission_in_user_recognized_pages(self):
        res = self.client.get(resolve_url('user_recognized_pages', user_id='test'), data={'keyword': 'keyword'})

        self.assertForbidden(res)
