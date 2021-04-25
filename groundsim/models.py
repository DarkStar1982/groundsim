from django.db import models
from django.contrib import admin

# satellite TLE record + system definition data
class Satellite(models.Model):
    satellite_name = models.CharField(max_length=24)
    satellite_tle1 = models.CharField(max_length=70)
    satellite_tle2 = models.CharField(max_length=70)
    norad_id = models.IntegerField(default=0, primary_key=True)
    config_subsystems = models.CharField(blank=True, max_length=4096)
    config_geometry = models.CharField(blank=True, max_length=4096)
    config_instrument = models.CharField(blank=True, max_length=4096)

class SatelliteInstance(models.Model):
    satellite_id = models.IntegerField(default=0) # should be a primary key?
    geometry = models.CharField(blank=True, max_length=4096)
    subsystems = models.CharField(blank=True, max_length=4096)
    instruments = models.CharField(blank=True, max_length=4096)

class SatelliteOrbitTrack(models.Model):
    satellite_ref = models.ForeignKey(Satellite, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)

class UserInstance(models.Model):
    user = models.CharField(max_length=128, null=True)
    email = models.CharField(max_length=128, null=True, unique=True)

class MissionScenario(models.Model):
    scenario_id = models.IntegerField(default=0, primary_key=True)
    start_date = models.DateTimeField(null=True, blank=True)
    mission_name = models.CharField(blank=True, max_length=255)
    description = models.CharField(blank=True, max_length=4096)
    initial_setup = models.CharField(blank=True, max_length=4096)
    objectives = models.CharField(blank=True, max_length=4096)

class MissionInstance(models.Model):
    mission_hash = models.CharField(max_length=64, primary_key=True)
    norad_id = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    mission_timer = models.IntegerField(default=0)
    tle_line_1 = models.CharField(blank=True, max_length=70)
    tle_line_2 = models.CharField(blank=True, max_length=70)
    satellite_ref = models.OneToOneField(SatelliteInstance, on_delete=models.CASCADE, null=True)
    user_ref = models.ForeignKey(UserInstance, on_delete=models.CASCADE, null=True)
    scenario_ref = models.ForeignKey(MissionScenario, on_delete=models.CASCADE, null=True)

class MissionEventLog(models.Model):
   mission_ref = models.ForeignKey(MissionInstance, on_delete=models.CASCADE, null=True)
   timestamp = models.DateTimeField(null=True, blank=True)
   message = models.CharField(blank=True, max_length=255)



admin.site.register(Satellite)
admin.site.register(MissionInstance)
admin.site.register(SatelliteInstance)
admin.site.register(UserInstance)
admin.site.register(MissionScenario)
admin.site.register(MissionEventLog)
admin.site.register(SatelliteOrbitTrack)
