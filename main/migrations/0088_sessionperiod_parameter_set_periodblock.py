# Generated by Django 4.2.18 on 2025-02-12 22:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0087_remove_parametersettreatment_revenues'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionperiod',
            name='parameter_set_periodblock',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_periods_b', to='main.parametersetperiodblock'),
        ),
    ]
