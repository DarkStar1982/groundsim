# Generated by Django 3.1.1 on 2020-12-15 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groundsim', '0008_auto_20201213_0027'),
    ]

    operations = [
        migrations.RenameField(
            model_name='satellite',
            old_name='geometry_definition',
            new_name='config_geometry',
        ),
        migrations.RenameField(
            model_name='satellite',
            old_name='instrument_definition',
            new_name='config_instrument',
        ),
        migrations.RenameField(
            model_name='satellite',
            old_name='system_definition',
            new_name='config_subsystems',
        ),
    ]
