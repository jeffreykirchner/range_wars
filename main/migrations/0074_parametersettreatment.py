# Generated by Django 4.2.18 on 2025-01-29 22:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0073_remove_parameterset_avatar_animation_speed_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterSetTreatment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_label', models.CharField(default='1', max_length=2, verbose_name='ID Label')),
                ('left_x', models.IntegerField(default=0, verbose_name='Left Verticy X')),
                ('left_y', models.IntegerField(default=0, verbose_name='Left Verticy Y')),
                ('middle_x', models.IntegerField(default=1, verbose_name='Middle Verticy X')),
                ('middle_y', models.IntegerField(default=2, verbose_name='Middle Verticy Y')),
                ('right_x', models.IntegerField(default=0, verbose_name='Right Verticy X')),
                ('right_y', models.IntegerField(default=2, verbose_name='Right Verticy Y')),
                ('range_width', models.IntegerField(default=2, verbose_name='Range Width')),
                ('range_height', models.IntegerField(default=2, verbose_name='Range Height')),
                ('costs', models.CharField(default='0,0,0,0', max_length=100, verbose_name='Costs')),
                ('revenues', models.CharField(default='0.25,0.25,0.25,0.25', max_length=100, verbose_name='Revenues')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameter_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_treatment', to='main.parameterset')),
            ],
            options={
                'verbose_name': 'Parameter Set Treatment',
                'verbose_name_plural': 'Parameter Set Treatmentss',
            },
        ),
    ]
