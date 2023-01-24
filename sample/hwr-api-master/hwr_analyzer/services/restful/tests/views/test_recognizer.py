import copy
import uuid
from typing import Dict
from unittest.mock import (
    MagicMock,
    patch,
)

import requests
from django.shortcuts import resolve_url
from parameterized import (
    parameterized,
    parameterized_class,
)
from rest_framework.test import APITestCase

from services.restful.documents.open_api_examples import (
    RECOGNIZE_PAGE_BY_NOTE_UUID,
    RECOGNIZE_PAGE_BY_PAGE_UUID,
    RECOGNIZE_STROKES,
)
from utils.authentications.credentials import (
    Credentials,
    CredentialsType,
)
from utils.testcases.assertion import AssertionMixin


# skipcq: PTC-W0046
class TestBase(APITestCase, AssertionMixin):
    @staticmethod
    def authenticate(client):
        client.force_authenticate(Credentials(username='test',
                                              credential_type=CredentialsType.USER_CREDENTIALS,
                                              is_active=True))


@patch('services.restful.views.recognizer.recognize_pages_async', return_value=MagicMock)
class TestRecognizeWithStrokes(TestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = resolve_url('recognize_strokes')

    def setUp(self) -> None:
        super().setUp()
        self.authenticate(self.client)
        self.request_body = copy.deepcopy(RECOGNIZE_STROKES.value)

    def test_response(self, recognize_pages_async):
        res = self.client.post(self.path, data=self.request_body)

        recognize_pages_async.apply_async.assert_called()

        self.assertOK(res)

    @parameterized.expand(
        [
            ('mimeType'),
            ('pages'),
        ],
    )
    def test_required_fields(self, _, field):
        self.request_body.pop(field)

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    @parameterized.expand(
        [
            ('mimeType', 1002),
            ('mimeType', '123456789123456789123456789123456789123456789123456789'),
            ('pages', 1002),
            ('pages', '123456789123456789123456789123456789123456789123456789'),
        ],
    )
    def test_field_is_invalid(self, _, field, value):
        self.request_body[field] = value

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    @parameterized.expand(
        [
            ('section'),
            ('owner'),
            ('bookCode'),
            ('pageNumber'),
            ('recognition'),
            ('strokes'),
        ],
    )
    def test_required_fields_in_page(self, _, field):
        self.request_body['pages'][0].pop(field)

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    @parameterized.expand(
        [
            ('section', '123456aa'),
            ('owner', '123456aa'),
            ('bookCode', '123456aa'),
            ('pageNumber', '123456aa'),
            ('recognition', '123456aa'),
            ('strokes', '123456aa'),
        ],
    )
    def test_field_is_invalid_in_page(self, _, field, value):
        self.request_body['pages'][0][field] = value

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    def test_response_when_iink_server_is_down(self, recognize_pages_async):
        recognize_pages_async.apply_async.side_effect = requests.RequestException

        res = self.client.post(self.path, data=self.request_body)

        self.assertInternalServer(res)


@parameterized_class(
    ('request_body', 'id_params'),
    [
        (RECOGNIZE_PAGE_BY_NOTE_UUID.value, ['noteUUID', 'pageNumber']),
        (RECOGNIZE_PAGE_BY_PAGE_UUID.value, ['pageUUID']),
    ],
)
@patch('services.restful.views.recognizer.recognize_pages_async')
class TestRecognizePage(TestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = resolve_url('recognize_pages')

    @staticmethod
    def get_strokes():
        return [
            {
                'noteUUID': str(uuid.uuid1()),
                'section': 1,
                'owner': 1,
                'bookCode': 1,
                'pageNumber': 1,
                'strokes': [
                    {
                        'version': 0,
                        'writeId': '',
                        'mac': '',
                        'penTipType': 0,
                        'updated': 0,
                        'strokeType': 0,
                        'thickness': 0,
                        'color': 0,
                        'deleteFlag': True,
                        'startTime': 0,
                        'dotCount': 10,
                        'dots': [],
                    },
                ],
            },
        ]

    def setUp(self) -> None:
        super().setUp()
        self.authenticate(self.client)
        self.request_body: Dict = copy.deepcopy(self.request_body)

    def test_response(self, recognize_pages_async):
        with (patch('services.restful.views.recognizer.create_task', return_value=MagicMock(_id='id')),
              patch('domain.ndp.services.ndp_requester.requests.get') as mock):
            mock.return_value.json.return_value = self.get_strokes()

            res = self.client.post(self.path, data=self.request_body)

            recognize_pages_async.apply_async.assert_called()
            self.assertOK(res)

    @parameterized.expand(
        [
            ('mimeType',),
            ('pages',),
        ],
    )
    def test_required_fields(self, _, field):
        self.request_body.pop(field)

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    @parameterized.expand(
        [
            ('mimeType', 1002),
            ('mimeType', '123456789123456789123456789123456789123456789123456789'),
            ('pages', 1002),
            ('pages', '123456789123456789123456789123456789123456789123456789'),
        ],
    )
    def test_field_is_invalid(self, _, field, value):
        self.request_body[field] = value

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    def test_required_fields_in_page(self, _):
        for param in self.id_params:
            self.request_body['pages'][0].pop(param)

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    def test_field_is_invalid_in_page(self, _):
        for param in self.id_params:
            self.request_body['pages'][0][param] = 'thisistext'

        res = self.client.post(self.path, data=self.request_body)

        self.assertInvalidParam(res)

    def test_response_when_ndp_is_down(self, _):
        with (patch('services.restful.views.recognizer.create_task', return_value=MagicMock(_id='id')),
              patch('domain.ndp.services.ndp_requester.requests.get', side_effect=requests.RequestException)):

            res = self.client.post(self.path, data=self.request_body)

        self.assertInternalServer(res)

    def test_response_when_iink_server_is_down(self, recognize_pages_async):
        recognize_pages_async.apply_async.side_effect = requests.RequestException
        with (patch('services.restful.views.recognizer.create_task', return_value=MagicMock(_id='id')),
              patch('domain.ndp.services.ndp_requester.requests.get') as mock):
            mock.return_value.json.return_value = self.get_strokes()

            res = self.client.post(self.path, data=self.request_body)

            self.assertInternalServer(res)


class TestPermission(TestBase):

    def test_permission_recognize_strokes(self):
        request_body = RECOGNIZE_STROKES.value

        res = self.client.post(resolve_url('recognize_strokes'), data=request_body)

        self.assertForbidden(res)

    def test_permission_recognize_page_by_note_uuid(self):
        request_body = RECOGNIZE_PAGE_BY_NOTE_UUID.value

        res = self.client.post(resolve_url('recognize_pages'), data=request_body)

        self.assertForbidden(res)

    def test_permission_recognize_page_by_page_uuid(self):
        request_body = RECOGNIZE_PAGE_BY_PAGE_UUID.value

        res = self.client.post(resolve_url('recognize_pages'), data=request_body)

        self.assertForbidden(res)
