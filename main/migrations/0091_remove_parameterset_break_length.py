# Generated by Django 4.2.18 on 2025-02-13 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0090_remove_parameterset_break_frequency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameterset',
            name='break_length',
        ),
    ]
