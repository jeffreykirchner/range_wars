# Generated by Django 4.2.18 on 2025-03-26 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0115_parametersettreatment_cost_percent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametersettreatment',
            name='cost_percent',
            field=models.DecimalField(decimal_places=4, default=0.1, max_digits=7, verbose_name='Scale Width'),
        ),
    ]
