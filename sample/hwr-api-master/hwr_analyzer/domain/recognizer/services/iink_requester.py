import json
from typing import (
    Dict,
    List,
)

import requests

from hwr_analyzer import settings

SerializedStroke = Dict


def recognize(
    strokes: List[SerializedStroke],
    content_type: str,
    width: int = settings.IINK_WIDTH,
    height: int = settings.IINK_HEIGHT,
    x_dpi: int = settings.IINK_XDPI,
    y_dpi: int = settings.IINK_YDPI,
    iink_config: Dict = {},  # skipcq: PYL-W0102
):
    request_body = {
        "xDPI": x_dpi,
        "yDPI": y_dpi,
        "width": width,
        "height": height,
        "contentType": content_type,
        "configuration": iink_config,
        "strokeGroups": [{"strokes": strokes}],
    }

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/vnd.myscript.jiix,application/json',
        'applicationKey': settings.IINK_SERVER_KEY,
        'userId': '',
        'hmac': 'hmac',
    }

    res = requests.post(settings.IINK_SERVER_URL,
                        headers=headers,
                        data=json.dumps(request_body))
    res.raise_for_status()
    return res
