from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_unique_bill_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='inshipment',
            name='export',
            field=models.BooleanField(default=False, help_text='Export status (False=in inventory, True=exported)'),
        ),
        migrations.AddField(
            model_name='inshipment',
            name='export_date',
            field=models.DateField(blank=True, help_text='Export date if exported', null=True),
        ),
    ]

