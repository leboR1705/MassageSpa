"""Remove addons field from Booking model.

Generated manually to drop the column added in initial migration.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('massage_app', '0008_alter_booking_service'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='addons',
        ),
    ]
