from django.urls import path

from services.restful.views.health_check import HealthCheckTaskView
from services.restful.views.recognized_pages import (
    RecognizedPagesView,
    RecognizedUserPagesView,
)
from services.restful.views.recognizer import (
    PageRecognizerView,
    StrokeRecognizerView,
    UserPageRecognizerView,
)
from services.restful.views.tasks import RecognitionTaskView
from services.restful.views.user_notes import UserNotesView
from services.restful.views.user_pages import UserPagesView

urlpatterns = [
    path('strokes/recognize', StrokeRecognizerView.as_view(), name='recognize_strokes'),
    path('pages/recognize', PageRecognizerView.as_view(), name='recognize_pages'),
    path('notes', UserNotesView.as_view(), name='user_notes'),
    path('notes/<str:note_uuid>/pages', UserPagesView.as_view(), name='user_pages'),
    path('recognition-tasks/<str:task_id>', RecognitionTaskView.as_view(), name='recognition_task'),
    path('pages', RecognizedPagesView.as_view(), name='recognized_pages'),

    path('users/<str:user_id>/pages/recognize', UserPageRecognizerView.as_view(), name='user_recognize_pages'),
    path('users/<str:user_id>/pages', RecognizedUserPagesView.as_view(), name='user_recognized_pages'),

    path('status', HealthCheckTaskView.as_view(), name='status'),
]
