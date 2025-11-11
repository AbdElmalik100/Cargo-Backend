from django.urls import re_path

from .stats import ShipmentsStatsConsumer

websocket_urlpatterns = [
    re_path(r'^ws/shipments/stats/$', ShipmentsStatsConsumer.as_asgi()),
]