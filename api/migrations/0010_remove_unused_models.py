from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_delete_outshipment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AdvancedShipmentLink',
        ),
        migrations.DeleteModel(
            name='AdvancedShipmentItem',
        ),
        migrations.DeleteModel(
            name='AdvancedShipment',
        ),
        migrations.DeleteModel(
            name='Item',
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
        migrations.DeleteModel(
            name='Warehouse',
        ),
    ]

