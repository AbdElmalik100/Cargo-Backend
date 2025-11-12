from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Max
from datetime import datetime

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
    
    def perform_create(self, serializer):
        serializer.save()
        notify_stats_update()
    
    def perform_update(self, serializer):
        serializer.save()
        notify_stats_update()
    
    def perform_destroy(self, instance):
        instance.delete()
        notify_stats_update()


class OutShipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for OutShipment model (Outbound Shipments)"""
    queryset = OutShipment.objects.prefetch_related('in_shipments').all()
    serializer_class = OutShipmentSerializer
    filterset_class = OutShipmentFilter

    search_fields = ["company_name", "sub_bill_number", "bill_number", "destination", "contract_status", "in_shipments__bill_number"]
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

    def perform_create(self, serializer):
        serializer.save()
        notify_stats_update()

    def perform_update(self, serializer):
        serializer.save()
        notify_stats_update()

    def perform_destroy(self, instance):
        # Get all linked inshipments before deletion
        in_shipment_ids = list(instance.in_shipments.values_list('id', flat=True))
        instance.delete()
        # Unmark all inshipments as exported
        InShipment.objects.filter(id__in=in_shipment_ids).update(export=False)
        notify_stats_update()


def notify_stats_update():
    """Push a signal to websocket listeners when shipment data changes"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "shipments_stats",
        {
            "type": "stats.update",
            "message": "update stats"
        }
    )


@receiver(post_save, sender=InShipment)
def in_shipment_saved(sender, instance, created, **kwargs):
    notify_stats_update()


@receiver(post_delete, sender=InShipment)
def in_shipment_removed(sender, instance, **kwargs):
    notify_stats_update()


@receiver(post_save, sender=OutShipment)
def out_shipment_saved(sender, instance, created, **kwargs):
    notify_stats_update()


@receiver(post_delete, sender=OutShipment)
def out_shipment_removed(sender, instance, **kwargs):
    notify_stats_update()

