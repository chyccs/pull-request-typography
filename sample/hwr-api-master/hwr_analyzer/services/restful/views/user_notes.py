from datetime import (
    datetime,
    timezone,
)

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from domain.ndp.services.ndp_requester import fetch_notes
from utils.response import APIResponse


class UserNotesView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def from_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    def serializer(self, note):
        data = {
            'id': note.id,
            'section': note.section,
            'owner': note.owner,
            'bookCode': note.book_code,
            'startPage': note.start_page,
            'endPage': note.end_page,
            'applicationId': note.application_id,
            'paperGroupId': note.paper_group_id,
            'description': note.description,
            'category': note.category,
            'cover': note.cover,
            'digital': note.digital,
            'hwrLang': note.hwr_lang,
            'lastStrokeAt': note.last_stroke_at,
            'lastStrokeUserId': note.last_stroke_user_id,
            'name': note.name,
            'pageNumber': note.page_number,
            'resourceOwnerId': note.resource_owner_id,
            'totalPages': note.total_pages,
            'userId': note.user_id,
            'usingPages': note.using_pages,
            'createdAt': self.from_timestamp(note.created_at),
            'modifiedAt': self.from_timestamp(note.modified_at),
            'active': note.active,
        }
        return data

    @extend_schema(exclude=True)
    def get(self, request):
        results = fetch_notes(request.user.username)
        return APIResponse(
            status=status.HTTP_200_OK,
            message='success',
            data=[self.serializer(result) for result in results],
        )
