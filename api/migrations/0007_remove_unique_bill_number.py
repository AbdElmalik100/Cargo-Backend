# Generated manually to remove unique constraints from bill_number

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_rename_shipment_advancedshipment_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='inshipment',
            name='unique_in_shipment_bill_number',
        ),
        migrations.RemoveConstraint(
            model_name='outshipment',
            name='unique_out_shipment_bill_number',
        ),
    ]


