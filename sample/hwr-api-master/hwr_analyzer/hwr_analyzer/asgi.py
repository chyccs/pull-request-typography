import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hwr_analyzer.settings')
django_asgi_app = get_asgi_application()

# skipcq: FLK-E402
from channels.routing import (
    ProtocolTypeRouter,
    URLRouter,
)

from services.websocket.routing import websocket_urlpatterns  # skipcq: FLK-E402
from utils.authentications.simple_authentication import TokenAuthMiddlewareStack  # skipcq: FLK-E402


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns,
        ),
    ),
})
