# Generated by Django 4.2.18 on 2025-03-25 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0110_alter_parametersettreatment_range_height_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersettreatment',
            name='values_count',
            field=models.IntegerField(default=100, verbose_name='Values Count'),
        ),
    ]
