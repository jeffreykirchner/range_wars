# Generated by Django 4.1.3 on 2022-11-15 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_sessionplayer_survey_complete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='current_experiment_phase',
            field=models.CharField(choices=[('Instructions', 'Instructions'), ('Run', 'Run'), ('Names', 'Names'), ('Done', 'Done')], default='Run', max_length=100),
        ),
    ]
