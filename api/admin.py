from django.contrib import admin
from .models import Destination, Company, InShipment, OutShipment

# Register your models here.

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']


# Register InShipment model
@admin.register(InShipment)
class InShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'bill_number', 'sub_bill_number', 'company_name', 
        'destination', 'contract_status', 'arrival_date', 'disbursement_date', 'created_at'
    ]
    list_filter = ['contract_status', 'created_at', 'arrival_date']
    search_fields = ['bill_number', 'sub_bill_number', 'company_name', 'destination', 'receiver_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


# Register OutShipment model
@admin.register(OutShipment)
class OutShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'bill_number', 'sub_bill_number', 'company_name', 
        'destination', 'export_date', 'disbursement_date', 'created_at'
    ]
    list_filter = ['created_at', 'export_date', 'arrival_date']
    search_fields = ['bill_number', 'sub_bill_number', 'company_name', 'destination', 'receiver_name', 'in_shipment__bill_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
