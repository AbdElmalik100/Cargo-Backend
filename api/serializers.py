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
        queryset=InShipment.objects.all(), write_only=True, source='in_shipment'
    )

    class Meta:
        model = OutShipment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'in_shipment']

    def validate(self, attrs):
        in_shipment = attrs.get('in_shipment') or getattr(self.instance, 'in_shipment', None)
        package_count = attrs.get('package_count') or getattr(self.instance, 'package_count', None)
        if in_shipment is None:
            raise serializers.ValidationError({"in_shipment_id": "يجب اختيار شحنة واردة."})
        if package_count is None or package_count <= 0:
            raise serializers.ValidationError({"package_count": "عدد الطرود مطلوب ويجب أن يكون أكبر من صفر."})
        remaining = max(0, int(in_shipment.package_count) - int(in_shipment.exported_count or 0))
        if package_count > remaining:
            raise serializers.ValidationError({
                "package_count": f"عدد الطرود المطلوب تصديره ({package_count}) يتجاوز المتبقي ({remaining})."
            })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        in_shipment = validated_data['in_shipment']
        export_date = validated_data.get('export_date') or date.today()
        validated_data['export_date'] = export_date

        out_shipment = OutShipment.objects.create(**validated_data)

        # Update inbound shipment exported_count and export flag
        in_shipment.exported_count = int(in_shipment.exported_count or 0) + int(out_shipment.package_count or 0)
        in_shipment.export = in_shipment.exported_count >= in_shipment.package_count
        in_shipment.save(update_fields=['exported_count', 'export', 'updated_at'])

        return out_shipment

    @transaction.atomic
    def update(self, instance, validated_data):
        raise serializers.ValidationError("لا يمكن تعديل الشحنة الصادرة بعد إنشائها.")
