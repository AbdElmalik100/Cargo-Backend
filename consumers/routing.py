from django.urls import re_path

from .shipments import ShipmentsConsumer

websocket_urlpatterns = [
    re_path(r'^ws/shipments/stats/$', ShipmentsConsumer.as_asgi()),
]