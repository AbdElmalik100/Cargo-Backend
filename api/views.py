from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Max
from django.db.models.deletion import ProtectedError
from datetime import datetime

from .models import Destination, Company, InShipment, OutShipment
from .serializers import (
    DestinationSerializer,
    CompanySerializer,
    InShipmentSerializer,
    OutShipmentSerializer,
)
from .filters import InShipmentFilter, OutShipmentFilter


class DestinationViewSet(viewsets.ModelViewSet):
    """ViewSet for Destination model - GET, POST, DELETE only (no PUT)"""
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    
    def update(self, request, *args, **kwargs):
        """Disable PUT/PATCH updates"""
        return Response(
            {"detail": "Method not allowed. Use DELETE and POST to modify destinations."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Disable PATCH updates"""
        return Response(
            {"detail": "Method not allowed. Use DELETE and POST to modify destinations."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company model - GET, POST, DELETE only (no PUT)"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    
    def update(self, request, *args, **kwargs):
        """Disable PUT/PATCH updates"""
        return Response(
            {"detail": "Method not allowed. Use DELETE and POST to modify companies."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Disable PATCH updates"""
        return Response(
            {"detail": "Method not allowed. Use DELETE and POST to modify companies."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class InShipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for InShipment model (Inbound Shipments)"""
    queryset = InShipment.objects.all()
    serializer_class = InShipmentSerializer
    filterset_class = InShipmentFilter

    search_fields = ["company_name", "sub_bill_number", "bill_number", "destination", "contract_status"]
    ordering_fields = ["disbursement_date", "arrival_date", "payment_fees"]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = InShipment.objects.aggregate(
            total_shipments=Count('id'),
            total_weight=Sum('weight'),
            total_payment_fees=Sum('payment_fees'),
            total_ground_fees=Sum('ground_fees'),
            last_updated=Max('updated_at'),
        )
        
        stats['total_shipments'] = stats['total_shipments'] or 0
        stats['total_weight'] = stats['total_weight'] or 0
        stats['total_payment_fees'] = stats['total_payment_fees'] or 0
        stats['total_ground_fees'] = stats['total_ground_fees'] or 0
        stats['last_updated'] = stats['last_updated'] or datetime.now()

        for key, value in stats.items():
            if key == 'total_shipments':
                continue
            elif key == 'last_updated':
                stats[key] = value.isoformat() if value else None
            else:   
                stats[key] = float(value or 0)

        return Response(stats)
    
    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            # Cannot delete an InShipment that is referenced by one or more OutShipments
            raise ValidationError({
                "detail": "لا يمكن حذف الشحنة الواردة لأنها مرتبطة بشحنات صادرة. احذف الشحنات الصادرة المرتبطة أولاً أو ألغِ العملية."
            })


class OutShipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for OutShipment model (Outbound Shipments)"""
    queryset = OutShipment.objects.select_related('in_shipment').all()
    serializer_class = OutShipmentSerializer
    filterset_class = OutShipmentFilter

    search_fields = ["company_name", "sub_bill_number", "bill_number", "destination", "contract_status", "in_shipment__bill_number"]
    ordering_fields = ["export_date", "disbursement_date", "arrival_date", "payment_fees"]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = OutShipment.objects.aggregate(
            total_shipments=Count('id'),
            total_weight=Sum('weight'),
            total_payment_fees=Sum('payment_fees'),
            total_ground_fees=Sum('ground_fees'),
            last_updated=Max('updated_at'),
        )
        
        stats['total_shipments'] = stats['total_shipments'] or 0
        stats['total_weight'] = stats['total_weight'] or 0
        stats['total_payment_fees'] = stats['total_payment_fees'] or 0
        stats['total_ground_fees'] = stats['total_ground_fees'] or 0
        stats['last_updated'] = stats['last_updated'] or datetime.now()

        for key, value in stats.items():
            if key == 'total_shipments':
                continue
            elif key == 'last_updated':
                stats[key] = value.isoformat() if value else None
            else:   
                stats[key] = float(value or 0)

        return Response(stats)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
