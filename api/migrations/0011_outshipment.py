from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_remove_unused_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutShipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_number', models.CharField(help_text='رقم البوليصة', max_length=100)),
                ('arrival_date', models.DateField(help_text='تاريخ الوصول')),
                ('sub_bill_number', models.CharField(help_text='رقم البوليصة الفرعية', max_length=100)),
                ('company_name', models.CharField(help_text='اسم الشركة', max_length=255)),
                ('package_count', models.PositiveIntegerField(help_text='عدد الطرود')),
                ('weight', models.DecimalField(decimal_places=2, help_text='الوزن', max_digits=10)),
                ('destination', models.CharField(help_text='الجهة', max_length=255)),
                ('payment_fees', models.DecimalField(decimal_places=2, help_text='رسوم الدفع', max_digits=10)),
                ('customs_certificate', models.CharField(help_text='الشهادة الجمركية', max_length=100)),
                ('contract_status', models.CharField(help_text='الحالة', max_length=255)),
                ('disbursement_date', models.DateField(blank=True, help_text='تاريخ الصرف (اختياري)', null=True)),
                ('receiver_name', models.CharField(help_text='المستلم', max_length=255)),
                ('ground_fees', models.DecimalField(decimal_places=2, help_text='رسوم الأرضية', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('export_date', models.DateField(blank=True, help_text='تاريخ التصدير', null=True)),
                ('in_shipment', models.OneToOneField(help_text='Inbound shipment associated with this outbound record', on_delete=django.db.models.deletion.CASCADE, related_name='out_shipment', to='api.inshipment')),
            ],
            options={
                'verbose_name': 'Outbound Shipment',
                'verbose_name_plural': 'Outbound Shipments',
                'db_table': 'out_shipments',
                'ordering': ['-created_at'],
            },
        ),
    ]

