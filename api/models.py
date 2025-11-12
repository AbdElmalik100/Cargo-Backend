from django.db import models

# Create your models here.


class Destination(models.Model):
    """Destination model for shipment destinations"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'destinations'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Company(models.Model):
    """Company model for shipment companies"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Base Shipment model with common fields
class BaseShipment(models.Model):
    """Base model with common fields for InShipment and OutShipment"""
    bill_number = models.CharField(max_length=100, help_text="رقم البوليصة")
    arrival_date = models.DateField(help_text="تاريخ الوصول")
    sub_bill_number = models.CharField(unique=True, max_length=100, help_text="رقم البوليصة الفرعية")
    company_name = models.CharField(max_length=255, help_text="اسم الشركة")
    package_count = models.PositiveIntegerField(help_text="عدد الطرود")
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="الوزن")
    destination = models.CharField(max_length=255, help_text="الجهة")
    payment_fees = models.DecimalField(max_digits=10, decimal_places=2, help_text="رسوم الدفع")
    customs_certificate = models.CharField(max_length=100, help_text="الشهادة الجمركية")
    contract_status = models.CharField(max_length=255, help_text="الحالة")
    disbursement_date = models.DateField(blank=True, null=True, help_text="تاريخ الصرف (اختياري)")
    receiver_name = models.CharField(max_length=255, help_text="المستلم")
    ground_fees = models.DecimalField(max_digits=10, decimal_places=2, help_text="رسوم الأرضية")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


# In Shipments model (Inbound Shipments)
class InShipment(BaseShipment):
    """Model for Inbound Shipments"""
    export = models.BooleanField(default=False, help_text="Export status (False=in inventory, True=exported)")
    
    class Meta:
        db_table = 'in_shipments'
        ordering = ['-created_at']
        verbose_name = 'Inbound Shipment'
        verbose_name_plural = 'Inbound Shipments'

    def __str__(self):
        return f"In Shipment {self.sub_bill_number} - {self.company_name}"


class OutShipment(BaseShipment):
    """Model for Outbound Shipments linked to multiple inbound shipments"""
    in_shipments = models.ManyToManyField(
        InShipment,
        related_name='out_shipments',
        help_text="Inbound shipments associated with this outbound record"
    )
    export_date = models.DateField(blank=True, null=True, help_text="تاريخ التصدير")

    class Meta:
        db_table = 'out_shipments'
        ordering = ['-created_at']
        verbose_name = 'Outbound Shipment'
        verbose_name_plural = 'Outbound Shipments'

    def __str__(self):
        return f"Out Shipment {self.sub_bill_number} - {self.company_name}"