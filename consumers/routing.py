from django.urls import re_path

from .shipments import ShipmentsConsumer

websocket_urlpatterns = [
    re_path(r'^ws/shipments/$', ShipmentsConsumer.as_asgi()),
]