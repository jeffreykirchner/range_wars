# Generated by Django 4.1.3 on 2022-11-28 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_parameterset_json_for_subject_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametersetplayer',
            name='json_for_subject',
        ),
        migrations.RemoveField(
            model_name='parametersetplayer',
            name='json_for_subject_update_required',
        ),
        migrations.RemoveField(
            model_name='parametersetplayer',
            name='json_index',
        ),
    ]
