# Generated by Django 4.2.18 on 2025-03-06 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0103_remove_parameterset_enable_chat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametersettreatment',
            name='scale_height',
        ),
    ]
