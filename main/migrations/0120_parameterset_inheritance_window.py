# Generated by Django 4.2.18 on 2025-03-26 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0119_remove_parametersettreatment_inheritance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='inheritance_window',
            field=models.IntegerField(default=10, verbose_name='Inheritance Window'),
        ),
    ]
