from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_inshipment_export_outshipment_in_shipment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OutShipment',
        ),
    ]

