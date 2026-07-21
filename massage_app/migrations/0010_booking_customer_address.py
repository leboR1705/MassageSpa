from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('massage_app', '0009_remove_booking_addons'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='customer_address',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
