# Generated by Django 4.2.11 on 2024-04-29 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_session_id_string'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameterset',
            name='private_chat',
        ),
    ]
