from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('massage_app', '0004_merge_20251122_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='status',
            field=models.CharField(max_length=20, choices=[('Active', 'Active'), ('On Leave', 'On Leave')], default='Active'),
        ),
    ]
