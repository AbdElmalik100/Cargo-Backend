import django_filters
from .models import InShipment, OutShipment


class InShipmentFilter(django_filters.FilterSet):
    """FilterSet for InShipment model"""
    bill_number = django_filters.CharFilter(lookup_expr='iexact')
    sub_bill_number = django_filters.CharFilter(lookup_expr='iexact')
    export = django_filters.BooleanFilter()
    
    class Meta:
        model = InShipment
        fields = ['bill_number', 'sub_bill_number', 'export']


class OutShipmentFilter(django_filters.FilterSet):
    """FilterSet for OutShipment model"""
    bill_number = django_filters.CharFilter(field_name='in_shipment__bill_number', lookup_expr='iexact')
    
    class Meta:
        model = OutShipment
        fields = ['bill_number']
    
    def filter_queryset(self, queryset):
        """Override to add distinct() for ManyToMany relationships"""
        queryset = super().filter_queryset(queryset)
        return queryset
