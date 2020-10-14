# Generated by Django 3.1.1 on 2020-10-11 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groundsim', '0002_satellite_norad_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='MissionInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mission_hash', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='SatelliteInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satellite_id', models.IntegerField(default=0)),
            ],
        ),
    ]