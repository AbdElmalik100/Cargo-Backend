from .views import DestinationViewSet, CompanyViewSet, InShipmentViewSet, OutShipmentViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()

router.register('destinations', DestinationViewSet, basename='destination')

router.register('companies', CompanyViewSet, basename='company')

router.register('in-shipments', InShipmentViewSet, basename='in-shipment')

router.register('out-shipments', OutShipmentViewSet, basename='out-shipment')

urlpatterns = [
    path("api/", include(router.urls)),
]

