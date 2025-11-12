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
    in_shipments = InShipmentSerializer(many=True, read_only=True)
    in_shipment_ids = serializers.PrimaryKeyRelatedField(
        queryset=InShipment.objects.all(),
        many=True,
        write_only=True,
        source='in_shipments'
    )

    class Meta:
        model = OutShipment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'in_shipments']

    def validate_in_shipment_ids(self, value):
        """Validate that inbound shipments are available unless already linked to current instance"""
        if not value:
            raise serializers.ValidationError("يجب اختيار شحنة واحدة على الأقل.")

        instance = getattr(self, 'instance', None)
        allowed_ids = set()
        if instance is not None:
            allowed_ids = set(instance.in_shipments.values_list('id', flat=True))

        exported_shipments = [s for s in value if s.export and s.id not in allowed_ids]
        if exported_shipments:
            exported_numbers = [s.sub_bill_number for s in exported_shipments]
            raise serializers.ValidationError(
                f"الشحنات التالية تم تصديرها بالفعل: {', '.join(exported_numbers)}"
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        in_shipments = validated_data.pop('in_shipments', [])
        if not in_shipments:
            raise serializers.ValidationError("يجب اختيار شحنة واحدة على الأقل.")

        export_date = validated_data.get('export_date') or date.today()
        validated_data['export_date'] = export_date

        # Create the outshipment
        out_shipment = OutShipment(**validated_data)
        out_shipment.save()
        
        # Link the inshipments
        out_shipment.in_shipments.set(in_shipments)
        
        # Mark all inshipments as exported
        InShipment.objects.filter(id__in=[s.id for s in in_shipments]).update(export=True)

        return out_shipment

    @transaction.atomic
    def update(self, instance, validated_data):
        in_shipments = validated_data.pop('in_shipments', None)
        export_date = validated_data.get('export_date') or instance.export_date or date.today()

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.export_date = export_date
        instance.save()

        # Update inshipments if provided
        if in_shipments is not None:
            # Unmark old inshipments as exported (except ones remaining selected later)
            old_shipment_ids = list(instance.in_shipments.values_list('id', flat=True))
            instance.in_shipments.set(in_shipments)
            new_ids = [s.id for s in in_shipments]
            removed_ids = set(old_shipment_ids) - set(new_ids)
            if removed_ids:
                InShipment.objects.filter(id__in=removed_ids).update(export=False)
            InShipment.objects.filter(id__in=new_ids).update(export=True)
        else:
            # Ensure exports remain True for existing links
            InShipment.objects.filter(id__in=instance.in_shipments.values_list('id', flat=True)).update(export=True)

        return instance

