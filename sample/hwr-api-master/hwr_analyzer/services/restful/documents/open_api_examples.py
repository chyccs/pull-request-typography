from drf_spectacular.utils import OpenApiExample

RECOGNITION_EXAMPLE = {
    "xDpi": 107.14286041259766,
    "height": 600.7586669921875,
    "contentType": "Text",
    "width": 430.67965698242188,
    "configuration": {},
    "language": "ko_KR",
    "yDpi": 107.14286041259766,
    "analyzer": {
        "separateShapesAndText": True,
        "blockSizeSamplingSteps": 3,
        "paperWidth": 155.50445556640625,
        "removeShape": False,
        "paperHeight": 215.51300048828125,
        "kindOfEngine": 0,
    },
    "scale": 10,
}

RECOGNIZE_PAGE_BY_NOTE_UUID = OpenApiExample(
    request_only=True,
    summary="noteUUID와 pageNumber로 요청",
    name="noteUUID와 pageNumber로 요청",
    value={
        "pages": [
            {
                "recognition": RECOGNITION_EXAMPLE,
                "queryType": "SNAPSHOT",
                "pageNumber": 2,
                "noteUUID": "08121ad2-1ea6-4033-b588-ff66f8358b97",
            },
        ],
        "mimeType": "application/vnd.neolab.ndp2.stroke+json",
    },
)

RECOGNIZE_PAGE_BY_PAGE_UUID = OpenApiExample(
    request_only=True,
    summary="pageUUID로 요청",
    name="pageUUID로 요청",
    value={
        "pages": [
            {
                "recognition": RECOGNITION_EXAMPLE,
                "queryType": "SNAPSHOT",
                "pageUUID": "6bb8f1b9-8a17-4dcc-927a-d51adc7decf1",
            },
        ],
        "mimeType": "application/vnd.neolab.ndp2.stroke+json",
    },
)

RECOGNIZE_STROKES = OpenApiExample(
    request_only=True,
    name="application/json",
    value={
        "pages": [
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
                        "dots": "AADHxsY+KVxbQXsUCkFaWgAAAPf29j4AAFxBmpkJQVpaAAAA//7",
                        "strokeType": 0,
                        "startTime": 1606711708278,
                    },
                ],
                "noteUUID": "",
            },
        ],
        "mimeType": "application/vnd.neolab.ndp2.stroke+json",
    },
)

RECOGNIZED = OpenApiExample(
    response_only=True,
    name="Await: True",
    value={
        "result": "success",
        "contents": [
            {
                "iink": {
                    "type": "Text",
                    "bounding-box": {
                        "x": 4.64444447,
                        "y": 283.749237,
                        "width": 129.585571,
                        "height": 29.6027222,
                    },
                    "label": "르네지라로 인간의 욕망 삼각구조 로 설명 with\nex\n, 세르반테스 t 돈키호테 태호",
                    "words": [
                        {
                            "label": "르네지라로",
                            "candidates": [
                                "르네지라로",
                                "르네지라도",
                            ],
                            "bounding-box": {
                                "x": 4.64444447,
                                "y": 283.749237,
                                "width": 27.2593765,
                                "height": 7.05209351,
                            },
                            "items": [
                                {
                                    "timestamp": "2020-11-30 04:48:28.278000",
                                    "X": [
                                        6.14441919,
                                        6.25836039,
                                        6.37159395,
                                        6.42909718,
                                        6.65520859,
                                        6.88203049,
                                        7.33531904,
                                        7.73181438,
                                        8.07186985,
                                        8.29798317,
                                        8.52480316,
                                        8.66590405,
                                    ],
                                    "Y": [
                                        285.724518,
                                        285.641296,
                                        285.614471,
                                        285.530518,
                                        285.505127,
                                        285.423309,
                                        285.287872,
                                        285.179932,
                                        285.071289,
                                        285.045898,
                                        284.964081,
                                    ],
                                    "F": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "T": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "type": "stroke",
                                    "id": "0000000001009300ff00",
                                },
                            ],
                        },
                    ],
                    "version": "3",
                    "id": "MainBlock",
                },
            },
        ],
    },
)

RECOGNITION_TASK_REGISTERED = OpenApiExample(
    response_only=True,
    name="Await: False",
    value={
        "result": "success",
        "taskId": "63834bb3beec048f80c339ec",
        "message": "registered",
    },
)

RECOGNIZED_PAGE = OpenApiExample(
    response_only=True,
    name="필기 인식된 페이지 검색 결과",
    value={
        "result": "success",
        "contents": [
            {
                "sectionCode": 3,
                "ownerCode": 27,
                "noteCode": 603,
                "noteUUID": "",
                "pageNumber": 3,
                "userId": "dev@neolab.net",
                "language": "ko_KR",
                "label": "우리가 이루어내야 하는 것 \"기능\" (그것은 어떠한가?) 활용'\n(대 사람들",
                "words": [],
            },
        ],
    },
)

RECOGNITION_TASK = OpenApiExample(
    response_only=True,
    name="필기 인식 작업 조회 결과",
    value={
        "task_id": "6bb8f1b9-8a17-4dcc-927a-d51adc7decf1",
        "status": "DONE",
        "request": {},
        "result": {},
        "requested_at": 1606711708278,
        "processed_at": 1606711708278,
    },
)
