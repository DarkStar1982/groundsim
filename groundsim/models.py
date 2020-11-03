from django.db import models
from django.contrib import admin

# satellite TLE record +
class Satellite(models.Model):
    satellite_name = models.CharField(max_length=24) # tle line 0
    satellite_tle1 = models.CharField(max_length=70)
    satellite_tle2 = models.CharField(max_length=70)
    norad_id = models.IntegerField(default=0)  # should be primary key!

class SatelliteInstance(models.Model):
    satellite_id = models.IntegerField(default=0) # not a primary key!
    geometry = models.CharField(blank=True, max_length=4096)
    subsystems = models.CharField(blank=True, max_length=4096)
    instruments = models.CharField(blank=True, max_length=4096)

class MissionInstance(models.Model):
    mission_hash = models.CharField(max_length=64, primary_key=True)
    norad_id = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    mission_timer = models.IntegerField(default=0)
    tle_line_1 = models.CharField(blank=True, max_length=70)
    tle_line_2 = models.CharField(blank=True, max_length=70)
    satellite_ref = models.OneToOneField(SatelliteInstance, on_delete=models.CASCADE, null=True)

class UserInstance(models.Model):
    user = models.CharField(max_length=128, null=True)
    email = models.CharField(max_length=128, null=True, unique=True)
    mission_ref = models.ForeignKey(MissionInstance, on_delete=models.CASCADE, null=True)

# class MissionEventLog(models.Model):
#   mission_hash = ForeignKey(MissionInstance)
#   timestamp = models.DateTimeField()
#   message = models.CharField(blank=True, max_length=255)

# class MissionScenario(models.Model):
#   satellite_id = models.IntegerField(default=0)
#   start_date = models.DateTimeField()
#   mission_name = models.CharField(blank=True, max_length=255)
#   timestamp = models.DateTimeField()
#   initial_conditions = models.CharField(blank=True, max_length=255)
#   objectives = models.CharField(blank=True, max_length=255)

admin.site.register(Satellite)
admin.site.register(MissionInstance)
admin.site.register(SatelliteInstance)
admin.site.register(UserInstance)
