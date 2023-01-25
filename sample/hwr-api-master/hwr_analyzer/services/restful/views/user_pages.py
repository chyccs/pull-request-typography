from datetime import (
    datetime,
    timezone,
)

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from domain.ndp.services.ndp_requester import fetch_pages
from utils.response import APIResponse


class UserPagesView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def from_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    def serializer(self, page):
        data = {
            'id': page.id,
            'name': page.name,
            'section': page.section,
            'owner': page.owner,
            'bookCode': page.book_code,
            'pageNumber': page.page_number,
            'noteId': page.note_id,
            'lastStrokeAt': page.last_stroke_at,
            'lastStrokeUserId': page.last_stroke_user_id,
            'digital': page.digital,
            'favorite': page.favorite,
            'transText': page.trans_text,
            'transTextWord': page.trans_text_word,
            'transTime': page.trans_time,
            'createdAt': self.from_timestamp(page.created_at),
            'modifiedAt': self.from_timestamp(page.modified_at),
        }
        return data

    @extend_schema(exclude=True)
    def get(self, request, note_uuid: str):
        results = fetch_pages(request.user.username, note_uuid)
        return APIResponse(
            status=status.HTTP_200_OK,
            message='success',
            data=[self.serializer(result) for result in results],
        )
