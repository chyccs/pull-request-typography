from typing import List
from unittest.mock import patch

from django.db import DatabaseError
from django.shortcuts import resolve_url
from pymongo import MongoClient
from rest_framework.test import APITestCase

from utils.testcases.assertion import AssertionMixin


class TestResponse(APITestCase, AssertionMixin):

    @staticmethod
    def build_path(resources: List[str] = []):  # skipcq: PYL-W0102
        path = '&'.join([f'resource={resource}' for resource in resources])
        return f'{resolve_url("status")}{"?" + path if resources else ""}'

    def test_response(self):

        res = self.client.get(self.build_path())

        self.assertOK(res)

    def test_response_when_db_is_up(self):

        res = self.client.get(self.build_path(['database']))

        self.assertOK(res)
        self.assertEqual(res.data['contents']['database'], 'UP')

    def test_failed_when_db_is_down(self):

        with patch.object(MongoClient, '__init__') as init:
            init.side_effect = DatabaseError
            res = self.client.get(self.build_path(['database']))

        self.assertServiceUnavailableError(res)
        self.assertEqual(res.data['contents']['data']['database'], 'OUT_OF_SERVICE')
