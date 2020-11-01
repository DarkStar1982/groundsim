# Generated by Django 3.1.1 on 2020-11-01 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groundsim', '0005_missioninstance_satellite_ref'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=128)),
                ('email', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='missioninstance',
            name='user_ref',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='groundsim.userinstance'),
        ),
    ]
