# Generated by Django 4.2.18 on 2025-02-05 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0086_alter_parametersetplayer_id_label'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametersettreatment',
            name='revenues',
        ),
    ]
