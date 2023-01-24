import json
from typing import (
    Any,
    Callable,
    Optional,
)

from channels.generic.websocket import WebsocketConsumer

from domain.analyzer.models.request_scheme import (
    PAGE_RECOGNIZE_SCHEME,
    STROKE_RECOGNIZE_SCHEME,
)
from domain.ndp.services.ndp_requester import (
    fetch_strokes_by_note,
    fetch_strokes_by_page,
)
from domain.recognizer.services.stroke_recognizer import recognize_pages_async
from hwr_analyzer.settings import (
    CELERY_RECOGNIZER_AWAIT_TIMEOUT,
    HWR_API_VALID_CONTENT_TYPE_LIST,
)
from services.restful.services import create_task
from utils import logging as logger
from utils.validation import validate_message


class StreamConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None

    def connect(self):
        self.user = self.scope["user"]
        self.accept()

    def disconnect(self, close_code):
        raise NotImplementedError()

    def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            command = data.get('command')
            payload = data.get('payload')
            headers = data.get('headers', {})
            if command == 'recognize_strokes':
                result = _recognize_strokes(headers=headers,
                                            payload=payload,
                                            user_id=self.user.get_username())
            elif command == 'recognize_pages':
                result = _recognize_pages(headers=headers,
                                          payload=payload,
                                          user_id=self.user.get_username())
            else:
                raise RuntimeError('Illegal command')

            self.send(text_data=json.dumps(result, ensure_ascii=False))
        except Exception as ex:  # skipcq: PYL-W0703
            self.send(text_data=json.dumps({
                "result": "error",
                "contents": str(ex),
            }, ensure_ascii=False))


@validate_message(body_schema=STROKE_RECOGNIZE_SCHEME)
def _recognize_strokes(headers: dict, payload: dict, user_id: str):
    return _recognize(body=payload,
                      wait_result=bool(headers.get('await', False)),
                      user_id=user_id)


@validate_message(body_schema=PAGE_RECOGNIZE_SCHEME)
def _recognize_pages(headers: dict, payload: dict, user_id: str):
    def collect_ink(pages, user_id: str):
        for page in pages:
            inks = (
                fetch_strokes_by_page(user_id=user_id,
                                      query_type=page.get('queryType', 'SNAPSHOT'),
                                      page_uuid=page.get('pageUUID')) if page.get('pageUUID')
                else fetch_strokes_by_note(user_id=user_id,
                                           query_type=page.get('queryType', 'SNAPSHOT'),
                                           note_uuid=page.get('noteUUID'),
                                           page_number=page.get('pageNumber'))
            )

            if len(inks) == 0:
                raise RuntimeError('Ink does not exists')

            ink = inks[0]
            page['section'] = ink.section
            page['owner'] = ink.owner
            page['bookCode'] = ink.book_code
            page['strokes'] = [{
                "deleteFlag": s.delete_flag,
                "startTime": s.start_time,
                "dotCount": s.dot_count,
                "dots": s.dots,
            } for s in ink.strokes]
        return pages

    return _recognize(body=payload,
                      wait_result=bool(headers.get('await', False)),
                      collect_ink=collect_ink,
                      user_id=user_id)


def _recognize(body,
               wait_result: bool,
               collect_ink: Optional[Callable[[Any, str], Any]] = None,
               user_id: Optional[str] = None):
    logger.info(msg='started', data={
        'wait_result': wait_result,
        'collect_ink': collect_ink,
        'user_id': user_id,
    })
    if body['mimeType'] not in HWR_API_VALID_CONTENT_TYPE_LIST:
        raise ValueError('mimeType is not allowed')

    pages = body['pages']

    if collect_ink and user_id:
        pages = collect_ink(pages, user_id)
        logger.info(msg='ink collected', data=pages)

    task = create_task(user_id, pages)
    logger.info(msg='task created', data=task)

    if wait_result:
        job = recognize_pages_async.apply_async([str(task.task_id)])
        logger.info(msg='wait recognize_pages_async', data=task)

        if result := job.get(timeout=CELERY_RECOGNIZER_AWAIT_TIMEOUT):
            return {
                "result": "success",
                "contents": json.loads(result),
            }
        raise RuntimeError('failed to recognize')

    recognize_pages_async.apply_async([str(task.task_id)], countdown=5)
    logger.info(msg='recognize_pages_async apply_async', data=task)

    return {
        "result": "success",
        "task_id": str(task.task_id),
        "message": "registered",
    }
