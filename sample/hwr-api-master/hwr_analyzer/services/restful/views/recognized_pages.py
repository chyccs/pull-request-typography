
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from services.restful.documents.open_api_examples import RECOGNIZED_PAGE
from services.restful.models import RecognizedDocument
from services.restful.serializers import (
    CommonResultSerializer,
    RecognizedDocumentSerializer,
)
from services.restful.services import has_permission_to_access_user
from utils.exceptions import InvalidAccessError
from utils.response import APIResponse
from utils.validation import (
    JsonSchema,
    validate_request,
)


class BaseRecognizedPagesView(APIView):
    permission_classes = [IsAuthenticated]

    GET_QUERY_PARAMS_SCHEMA = JsonSchema.object(
        {
            'keyword': JsonSchema.array(JsonSchema.string(1, 50), max_items=1),
        },
        required=['keyword'],
        additional_properties=False,
    )

    @staticmethod
    def __serializer(doc):
        data = {
            'sectionCode': doc['section_code'],
            'ownerCode': doc['owner_code'],
            'noteCode': doc['note_code'],
            'noteUUID': doc['note_uuid'],
            'pageNumber': doc['page_number'],
            'userId': doc.get('user_id', None),
            'language': doc['language'],
            'label': doc['label'],
            'words': [{'label': word['label'],
                       'candidates': [{'rank': c['rank'], 'label': c['label']} for c in word.get('candidates')],
                       } for word in doc.get('words', [])],
        }
        return data

    @staticmethod
    def _find_recognized_document(keyword, user_id):
        return list(RecognizedDocument.objects.mongo_find({'$and': [
            {"user_id": user_id},
            {"words.label": {'$regex': keyword}},
        ]}))

    def _handle(self, request, user_id=None):
        keyword = request.query_params.get('keyword')
        if request.user.is_service_credentials:
            results = self._find_recognized_document(keyword, user_id)
            if not has_permission_to_access_user(service_user_id=request.user.username,
                                                 user_id=user_id):
                raise InvalidAccessError(f'has no permission to access {user_id}')
        else:
            results = self._find_recognized_document(keyword, request.user.username)

        return APIResponse(
            status=status.HTTP_200_OK,
            message='success',
            data=[self.__serializer(result) for result in results],
        )


class RecognizedPagesView(BaseRecognizedPagesView):

    @extend_schema(
        tags=['Pages'],
        operation_id='Search recognized pages',
        description='필기 인식된 페이지 검색',
        responses={status.HTTP_200_OK: RecognizedDocumentSerializer,
                   status.HTTP_400_BAD_REQUEST: CommonResultSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: CommonResultSerializer},
        request={},
        parameters=[
            OpenApiParameter(
                name="keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색어",
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
        examples=[RECOGNIZED_PAGE],
    )
    @validate_request(query_params_schema=BaseRecognizedPagesView.GET_QUERY_PARAMS_SCHEMA)
    def get(self, request):
        return self._handle(request)


class RecognizedUserPagesView(BaseRecognizedPagesView):

    @extend_schema(
        tags=['Pages'],
        operation_id='Search recognized pages (Using service credentials)',
        description='소속 유저의 필기 인식된 페이지 검색',
        responses={status.HTTP_200_OK: RecognizedDocumentSerializer,
                   status.HTTP_400_BAD_REQUEST: CommonResultSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: CommonResultSerializer},
        parameters=[
            OpenApiParameter(
                name="keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색어",
                required=True,
            ),
            OpenApiParameter(
                name="user_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="소속 유저 아이디",
                required=True,
            ),
        ],
        examples=[RECOGNIZED_PAGE],
    )
    @validate_request(query_params_schema=BaseRecognizedPagesView.GET_QUERY_PARAMS_SCHEMA)
    def get(self, request, user_id):
        return self._handle(request, user_id)
