# Generated by Django 4.2.18 on 2025-02-13 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0088_sessionperiod_parameter_set_periodblock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameterset',
            name='period_count',
        ),
    ]
