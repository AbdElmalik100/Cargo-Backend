from datetime import date
from rest_framework import serializers
from django.db import transaction
from .models import Destination, Company, InShipment, OutShipment


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class BaseShipmentSerializer(serializers.ModelSerializer):
    """Base serializer with common fields and validation"""
    status = serializers.SerializerMethodField()
    
    class Meta:
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
    
    def get_status(self, obj):
        """Calculate status based on disbursement_date"""
        return bool(obj.disbursement_date)
    
    def validate_bill_number(self, value):
        if not value:
            raise serializers.ValidationError("رقم البوليصة مطلوب")
        return value


class InShipmentSerializer(BaseShipmentSerializer):
    class Meta:
        model = InShipment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']


class OutShipmentSerializer(BaseShipmentSerializer):
    in_shipment = InShipmentSerializer(read_only=True)
    in_shipment_id = serializers.PrimaryKeyRelatedField(
        queryset=InShipment.objects.all(),
        write_only=True,
        source='in_shipment'
    )

    class Meta:
        model = OutShipment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'in_shipment']

    def _copy_from_in_shipment(self, out_shipment, in_shipment):
        """Copy shared fields from the inbound shipment"""
        fields_to_copy = [
            'bill_number', 'arrival_date', 'sub_bill_number', 'company_name',
            'package_count', 'weight', 'destination', 'payment_fees',
            'customs_certificate', 'contract_status', 'disbursement_date',
            'receiver_name', 'ground_fees',
        ]
        for field in fields_to_copy:
            setattr(out_shipment, field, getattr(in_shipment, field))

    @transaction.atomic
    def create(self, validated_data):
        in_shipment = validated_data['in_shipment']
        if hasattr(in_shipment, 'out_shipment'):
            raise serializers.ValidationError("تم إنشاء شحنة تصدير بالفعل لهذه الشحنة الواردة.")

        export_date = validated_data.get('export_date') or date.today()
        validated_data['export_date'] = export_date

        out_shipment = OutShipment(**validated_data)
        self._copy_from_in_shipment(out_shipment, in_shipment)
        out_shipment.save()

        in_shipment.export = True
        in_shipment.save(update_fields=['export', 'updated_at'])

        return out_shipment

    @transaction.atomic
    def update(self, instance, validated_data):
        in_shipment = validated_data.get('in_shipment', instance.in_shipment)
        export_date = validated_data.get('export_date') or instance.export_date or date.today()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        self._copy_from_in_shipment(instance, in_shipment)
        instance.export_date = export_date
        instance.save()

        in_shipment.export = True
        in_shipment.save(update_fields=['export', 'updated_at'])

        return instance

