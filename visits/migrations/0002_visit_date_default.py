from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('visits', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
