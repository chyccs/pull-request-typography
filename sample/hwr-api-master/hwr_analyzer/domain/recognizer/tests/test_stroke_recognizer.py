
import binascii
import json
import random
from unittest import TestCase

import requests
import responses

from domain.recognizer.services.stroke_recognizer import recognize_pages_async
from hwr_analyzer.settings import IINK_SERVER_URL
from services.restful.documents.open_api_examples import RECOGNITION_EXAMPLE
from services.restful.models import (
    RecognitionTasks,
    RecognitionTaskStatus,
)
from utils.test_factories.task import RecognitionTaskFactory
from utils.testcases.assertion import AssertionMixin

REQUEST_EXAMPLE = [
    {
        "owner": 27,
        "recognition": RECOGNITION_EXAMPLE,
        "pageNumber": 43,
        "section": 3,
        "bookCode": 603,
        "strokes": [
            {
                "penTipType": 0,
                "mac": "",
                "updated": 1652778939133,
                "version": 1,
                "writeId": "",
                "thickness": 0.10000000149011612,
                "deleteFlag": 0,
                "color": 4279834905,
                "strokeUUID": 0,
                "dotCount": 74,
                "dots": 'AADf3t4+w/XIQexReEFaWgAAAOvq6j7sUchBH4V7QVpaAAAA7+7uPo/'
                        'Cx0F7FH5BWloAAADx8PA+AADIQeF6gEFaWgAAAPHw8D7sUchBmpmBQV'
                        'paAAAA7+7uPsP1yEH2KIJBWloAAADv7u4+AADKQXE9gkFaWgAAAO/u7'
                        'j7sUcpBj8KBQVpaAAAA7+7uPuxRykG4HoFBWloAAADt7Ow+cT3KQXE9'
                        'gEFaWgAAAOno6D6PwslBcT1+QVpaAAAA5+bmPrgeyUHsUXxBWloAAAD'
                        'n5uY+w/XIQSlce0FaWgAAAOfm5j5I4chBUrh6QVpaAAAA5+bmPj0KyU'
                        'GamXlBWloAAADp6Og+FK7JQc3MeEFaWgAAAOPi4j49CstBH4V3QVpaA'
                        'AAA3dzcPmZmzEFI4XZBWloAAADZ2Ng+KVzNQXE9dkFaWgAAANnY2D6P'
                        'ws1BcT12QVpaAAAA7+7uPvYozkFI4XZBWloAAADx8PA+9ijOQexReEF'
                        'aWgAAAPX09D72KM5BcT16QVpaAAAA9fT0PvYozkGkcH1BWloAAAD39v'
                        'Y+exTOQWZmgEFaWgAAAPf29j4AAM5Bj8KBQVpaAAAA8/LyPo/CzUGkc'
                        'INBWloAAADd3Nw+j8LNQexRhEFaWgAAAJOSkj6Pws1B4XqEQVpaAAAA'
                        'ychIPo/CzUHsUYRBWloAAADJyEg+j8LNQexRhEFaWgAAAMnISD6Pws1'
                        'B7FGEQVpaAA==',
                'strokeType': 0,
                'startTime': 1606711708278,
            },
        ],
        "noteUUID": "",
    },
]

RESULT_EXAMPLE = {
    "type": "Raw Content",
    "id": "MainBlock",
    'bounding-box': {
        'height': 7.50680542,
        'width': 18.1488686,
        'x': 4.37444448,
        'y': 283.479248,
    },
    'elements': [
        {
            "type": "Raw Content",
            "kind": "text",
            'bounding-box': {
                'x': 4.37444448,
                'y': 283.479248,
                'width': 18.1488686,
                'height': 7.50680542,
            },
            "id": 'raw-content/10',
            "items": [
                {
                    "timestamp": "2021-08-31 15:14:39.652000",
                    "X": [58.5874977, 58.7666626, 58.7666626, 58.7666626, 58.7666626,
                          58.7666626, 58.9458313, 58.9458313, 59.1249962, 59.4833298,
                          59.8416634, 60.0208321, 60.0208321, 60.0208321, 60.0208321,
                          60.1999969, 60.1999969, 60.3791618, 60.5583305, 60.5583305],
                    "Y": [33.0518494, 33.0518494, 33.5907364, 34.1296272, 34.8481445,
                          35.5666618, 36.6444397, 37.5425873, 39.159256, 40.7759209,
                          42.033329, 43.4703674, 44.7277718, 46.3444405, 47.4222183,
                          48.6796265, 49.9370308, 50.4759216, 51.0148087, 51.0148087],
                    "F": [0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0],
                    "T": [0, 14, 30, 38, 46, 54, 62, 70,
                          78, 86, 94, 102, 110, 118, 126, 134,
                          142, 150, 158, 166],
                    "type": "stroke",
                    "id": "0000010001002900ff00",
                },
            ],
        },
    ],
}


class TestRecognizer(TestCase, AssertionMixin):
    def setUp(self) -> None:
        super().setUp()
        request = json.dumps(REQUEST_EXAMPLE.copy(), ensure_ascii=False)
        self.recognition_task = RecognitionTaskFactory.create(requested_by='test',
                                                              request=request)

    @responses.activate
    def test_success(self):
        responses.add(
            method=responses.POST,
            url=IINK_SERVER_URL,
            json=RESULT_EXAMPLE,
            status=200,
        )
        responses.add(
            method=responses.POST,
            url=IINK_SERVER_URL,
            json=RESULT_EXAMPLE,
            status=200,
        )

        recognize_pages_async(self.recognition_task.task_id)

        self.recognition_task.refresh_from_db()
        self.assertEqual(self.recognition_task.status, RecognitionTaskStatus.DONE)
        self.assertIsNotNone(self.recognition_task.request)
        self.assertIsNotNone(self.recognition_task.result)

    @responses.activate
    def test_failure_iink_is_down(self):
        responses.add(
            method=responses.POST,
            url=IINK_SERVER_URL,
            body=Exception('Request Exception'),
        )

        with self.assertRaises(Exception):
            recognize_pages_async(self.recognition_task.task_id)

    @responses.activate
    def test_failure_iink_is_in_invalid_status(self):
        responses.add(
            method=responses.POST,
            url=IINK_SERVER_URL,
            status=400,
        )

        with self.assertRaises(requests.HTTPError):
            recognize_pages_async(self.recognition_task.task_id)

    def test_failure_dot_is_invalid(self):
        request = json.loads(self.recognition_task.request)
        request[0]['strokes'][0]['dots'] = 'AADf3t4+w/XIQexReEFaWgAAr'
        self.recognition_task.request = json.dumps(request, ensure_ascii=False)
        self.recognition_task.save()

        with self.assertRaises(binascii.Error):
            recognize_pages_async(self.recognition_task.task_id)

    def test_recognition_task_does_not_exists(self):

        with self.assertRaises(RecognitionTasks.DoesNotExist):
            recognize_pages_async(random.randbytes(12).hex())
