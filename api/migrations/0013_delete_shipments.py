# Generated migration to remove legacy Shipments model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_remove_export_date_from_inshipment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Shipments',
        ),
    ]

