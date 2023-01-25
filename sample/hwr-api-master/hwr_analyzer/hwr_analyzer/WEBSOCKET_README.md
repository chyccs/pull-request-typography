## NDP Natural Handwriting Recognition Websocket API

###### &nbsp;
### Connecting
---

```http
GET wss://hwr.neolab.net/ws
```

###### &nbsp;
### Frame of message
---

```json   
{
    "command": "<command>", 
    "headers": {"key1": "value1", "key2": "value2"},
    "payload": {},
}
```

#### &nbsp;

### Authentication

---
Authentication works while a connection is established.

###### &nbsp;

##### Two-way authentication

*1. Same as Rest-API, authenticate with bearer token in http request header*

```http
GET /ws HTTP/1.1
Host: hwr.neolab.net
Authorization: Bearer <access-token>
```

*2. This can be done through authorization handshaking*

```json
{
    "command": "authorization", 
    "payload": {
        "token": "<access-token>"
    },
}
```

###### &nbsp;

### Handwriting recognition request 

---
Handwriting recognition with strokes

```json
{
    "command": "recognize_strokes", 
    "payload": {
        "pages": [
            {
                "recognition": {
                    "xDpi": 107.14286041259766,
                    "height": 600.7586669921875,
                    "contentType": "Text",
                    "width": 430.67965698242188,
                    "configuration": {},
                    "language": "ko_KR",
                    "yDpi": 107.14286041259766,
                    "analyzer": {
                        "separateShapesAndText": true,
                        "blockSizeSamplingSteps": 3,
                        "paperWidth": 155.50445556640625,
                        "removeShape": false,
                        "paperHeight": 215.51300048828125,
                        "kindOfEngine": 0
                    },
                    "scale": 10
                },
                "pageNumber": 11,
                "section": 3,
                "bookCode": 603,
                "strokes": [
                    {
                        "penTipType": 0,
                        "mac": "",
                        "updated": 1652662397574,
                        "version": 1,
                        "writeId": "",
                        "thickness": 0.10000000149011612,
                        "deleteFlag": 0,
                        "color": 4279834905,
                        "strokeUUID": 0,
                        "dotCount": 15,
                        "dots": "AADPzs4+Urg6QcP1REFaWgAAAPHw8D4pXDtBzcxEQVpaAAAA9fT0AAAzcxMPs3MUEF7FEJBWloA",
                        "strokeType": 0,
                        "startTime": 1604301385082
                    }
                ]
            }
        ],
        "mimeType": "application\/vnd.neolab.ndp2.stroke+json"
    }
}
```

Handwriting recognition with inkstore page reference

```json
{
    "command": "recognize_pages", 
    "payload": {
        "pages": [
            {
                "recognition": {
                    "xDpi": 107.14286041259766,
                    "height": 600.7586669921875,
                    "contentType": "Text",
                    "width": 430.67965698242188,
                    "configuration": {},
                    "language": "ko_KR",
                    "yDpi": 107.14286041259766,
                    "analyzer": {
                        "separateShapesAndText": true,
                        "blockSizeSamplingSteps": 3,
                        "paperWidth": 155.50445556640625,
                        "removeShape": false,
                        "paperHeight": 215.51300048828125,
                        "kindOfEngine": 0,
                    },
                    "scale": 10,
                },
                "pageNumber": 1,
                "noteUUID": "6b7d3ed0-ce98-44b4-b6ce-c25a78461088",
            },
        ],
        "mimeType": "application\/vnd.neolab.ndp2.stroke+json",
    },
}
```

###### &nbsp;

### Page Searching

---
Searching for pages handwriting recognized by keyword

```json
{
    "command": "search",
    "payload": {
        "keyword": "text"
    }
}
```
