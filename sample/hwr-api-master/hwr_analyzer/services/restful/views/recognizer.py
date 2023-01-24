import json
from typing import (
    Any,
    Callable,
    Optional,
)

from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

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
    DEBUG,
    HWR_API_VALID_CONTENT_TYPE_LIST,
    TESTING,
)
from services.restful.documents.open_api_examples import (
    RECOGNITION_TASK_REGISTERED,
    RECOGNIZE_PAGE_BY_NOTE_UUID,
    RECOGNIZE_PAGE_BY_PAGE_UUID,
    RECOGNIZE_STROKES,
    RECOGNIZED,
)
from services.restful.serializers import (
    CommonResultSerializer,
    PagesSerializer,
    PagesWithStrokesSerializer,
    RecognitionResultSerializer,
)
from services.restful.services import create_task
from utils import logging as logger
from utils.exceptions import NotFoundError
from utils.response import APIResponse
from utils.validation import validate_request


class BaseRecognizerView(APIView):

    @staticmethod
    def handle(request,
               wait_result: bool,
               collect_ink: Optional[Callable[[Any, str], Any]] = None,
               user_id: Optional[str] = None):
        logger.info(msg='started', data={
            'wait_result': wait_result,
            'collect_ink': collect_ink,
            'user_id': user_id,
        })
        user = user_id or request.user.username

        body = request.data
        if body['mimeType'] not in HWR_API_VALID_CONTENT_TYPE_LIST:
            raise ValueError('mimeType is not allowed')

        pages = body['pages']

        if collect_ink:
            pages = collect_ink(pages, user)
            logger.info(msg='ink collected', data=pages)

        task = create_task(user, pages)
        logger.info(msg='task created', data=task)

        if DEBUG and not TESTING:
            result = recognize_pages_async(str(task.task_id))
            return APIResponse(
                status=status.HTTP_200_OK,
                message='success',
                data=json.loads(result),
            )

        if wait_result:
            job = recognize_pages_async.apply_async([str(task.task_id)])
            logger.info(msg='wait recognize_pages_async', data=task)
            result = job.get(timeout=CELERY_RECOGNIZER_AWAIT_TIMEOUT, propagate=True)
            return APIResponse(
                status=status.HTTP_200_OK,
                message='success',
                data=json.loads(result),
            )

        recognize_pages_async.apply_async([str(task.task_id)], countdown=5)
        logger.info(msg='recognize_pages_async apply_async', data=task)
        return APIResponse(
            status=status.HTTP_200_OK,
            message='success',
            task_id=str(task.task_id),
        )


class PageRecognizerView(BaseRecognizerView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def collect_ink(pages, user_id):
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
                raise NotFoundError('Ink does not exists')

            ink = inks[0]
            page['section'] = ink.section
            page['owner'] = ink.owner
            page['bookCode'] = ink.book_code
            page['pageNumber'] = ink.page_number
            page['noteUUID'] = ink.note_uuid
            page['strokes'] = [{
                "deleteFlag": s.delete_flag,
                "startTime": s.start_time,
                "dotCount": s.dot_count,
                "dots": s.dots,
            } for s in ink.strokes]
        return pages

    @extend_schema(
        tags=['Recognizer'],
        operation_id='Recognize handwriting page',
        description='페이지 필기 인식',
        responses={status.HTTP_200_OK: RecognitionResultSerializer,
                   status.HTTP_400_BAD_REQUEST: CommonResultSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: CommonResultSerializer},
        request={'application/json': PagesSerializer},
        parameters=[
            OpenApiParameter(
                name="User",
                type=str,
                location=OpenApiParameter.HEADER,
                description="인증할 유저 아이디 (테스트 전용)",
                required=False,
                deprecated=True,
            ),
            OpenApiParameter(
                name="Await",
                type=bool,
                location=OpenApiParameter.HEADER,
                description="태스크 처리 종료 까지 대기 (테스트 전용)",
                required=False,
                deprecated=True,
            ),
        ],
        examples=[RECOGNIZE_PAGE_BY_NOTE_UUID,
                  RECOGNIZE_PAGE_BY_PAGE_UUID,
                  RECOGNIZED,
                  RECOGNITION_TASK_REGISTERED],
    )
    @validate_request(body_schema=PAGE_RECOGNIZE_SCHEME)
    def post(self, request, user_id=None):
        return self.handle(request=request,
                           wait_result=bool(request.META.get('HTTP_AWAIT', False)),
                           collect_ink=self.collect_ink,
                           user_id=user_id)


class UserPageRecognizerView(PageRecognizerView):
    @extend_schema(
        tags=['Recognizer'],
        operation_id='Recognize handwriting page (Using service credentials)',
        description='소속 유저의 페이지 필기 인식',
        responses={status.HTTP_200_OK: RecognitionResultSerializer,
                   status.HTTP_400_BAD_REQUEST: CommonResultSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: CommonResultSerializer},
        request={'application/json': PagesSerializer},
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="소속 유저 아이디",
                required=True,
            ),
            OpenApiParameter(
                name="User",
                type=str,
                location=OpenApiParameter.HEADER,
                description="인증할 유저 아이디 (테스트 전용)",
                required=False,
                deprecated=True,
            ),
            OpenApiParameter(
                name="Await",
                type=bool,
                location=OpenApiParameter.HEADER,
                description="태스크 처리 종료 까지 대기 (테스트 전용)",
                required=False,
                deprecated=True,
            ),
        ],
        examples=[RECOGNIZE_PAGE_BY_NOTE_UUID,
                  RECOGNIZE_PAGE_BY_PAGE_UUID,
                  RECOGNIZED,
                  RECOGNITION_TASK_REGISTERED],
    )
    @validate_request(body_schema=PAGE_RECOGNIZE_SCHEME)
    def post(self, request, user_id=None):
        return super().post(request, user_id)


class StrokeRecognizerView(BaseRecognizerView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Recognizer'],
        operation_id='Recognize handwriting stroke',
        description='스트로크 컬렉션 필기 인식',
        responses={status.HTTP_200_OK: RecognitionResultSerializer,
                   status.HTTP_400_BAD_REQUEST: CommonResultSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: CommonResultSerializer},
        request={'application/json': PagesWithStrokesSerializer},
        parameters=[
            OpenApiParameter(
                name="User",
                type=str,
                location=OpenApiParameter.HEADER,
                description="인증할 유저 아이디 (테스트 전용)",
                required=False,
                deprecated=True,
            ),
            OpenApiParameter(
                name="Await",
                type=bool,
                location=OpenApiParameter.HEADER,
                description="태스크 처리 종료 까지 대기 (테스트 전용)",
                required=False,
                deprecated=True,
            ),
        ],
        examples=[RECOGNIZE_STROKES,
                  RECOGNIZED,
                  RECOGNITION_TASK_REGISTERED],
    )
    @validate_request(body_schema=STROKE_RECOGNIZE_SCHEME)
    def post(self, request):
        return self.handle(request=request,
                           wait_result=bool(request.META.get('HTTP_AWAIT', False)))
