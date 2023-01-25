import json

from bson.errors import InvalidId
from bson.objectid import ObjectId
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from services.restful.documents.open_api_examples import RECOGNITION_TASK
from services.restful.models import RecognitionTasks
from services.restful.serializers import (
    CommonResultSerializer,
    RecognitionTaskSerializer,
)
from services.restful.services import has_permission_to_access_user
from utils import logging as logger
from utils.exceptions import InvalidAccessError
from utils.exceptions.bad_request import InvalidParamError
from utils.exceptions.not_found import ObjectNotFoundError
from utils.response import APIResponse


class RecognitionTaskView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def __serialize(task: RecognitionTasks):
        data = {
            'taskId': str(task.task_id),
            'status': task.status,
            'request': json.loads(task.request) if task.request else None,
            'result': json.loads(task.result) if task.result else None,
            'requestedAt': task.requested_at,
            'processedAt': task.processed_at,
        }
        return data

    @extend_schema(
        tags=['Tasks'],
        operation_id='Fetch recognition tasks',
        description='필기 인식 작업 조회',
        responses={status.HTTP_200_OK: RecognitionTaskSerializer,
                   status.HTTP_400_BAD_REQUEST: CommonResultSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: CommonResultSerializer},
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="작업 아이디",
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
        ],
        examples=[RECOGNITION_TASK],
    )
    def get(self, request, task_id):
        try:
            if request.user.is_service_credentials:
                task = RecognitionTasks.objects.get(pk=ObjectId(task_id))
                if not has_permission_to_access_user(service_user_id=request.user.username, user_id=task.requested_by):
                    raise InvalidAccessError()
            else:
                task = RecognitionTasks.objects.get(pk=ObjectId(task_id),
                                                    requested_by=request.user.username)
            return APIResponse(
                status=status.HTTP_200_OK,
                message='success',
                data=self.__serialize(task),
            )

        except RecognitionTasks.DoesNotExist as not_found_error:
            logger.error(msg="error occurred", err=not_found_error)
            raise ObjectNotFoundError(RecognitionTasks)

        except InvalidId as ex:
            logger.error(msg="invalid id error occurred", err=ex)
            raise InvalidParamError(message='Task\'s id is invalid.')
