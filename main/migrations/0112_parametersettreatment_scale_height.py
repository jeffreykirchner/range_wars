# Generated by Django 4.2.18 on 2025-03-25 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0111_parametersettreatment_values_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersettreatment',
            name='scale_height',
            field=models.DecimalField(decimal_places=4, default=2, max_digits=7, verbose_name='Scale Height'),
        ),
    ]
