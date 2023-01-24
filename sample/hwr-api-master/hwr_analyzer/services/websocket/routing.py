from django.urls import re_path

from services.websocket.consumer import StreamConsumer

websocket_urlpatterns = [
    re_path('ws', StreamConsumer.as_asgi()),
]
