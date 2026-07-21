from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('massage_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='notification_seen',
            field=models.BooleanField(default=False),
        ),
    ]
