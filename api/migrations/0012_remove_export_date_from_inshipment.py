from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_outshipment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inshipment',
            name='export_date',
        ),
    ]

