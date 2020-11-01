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

class UserInstance(models.Model):
    user = models.CharField(max_length=128)
    email = models.CharField(max_length=128)

class MissionInstance(models.Model):
    mission_hash = models.CharField(max_length=64) # primary key!
    norad_id = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    mission_timer = models.IntegerField(default=0)
    tle_line_1 = models.CharField(blank=True, max_length=70)
    tle_line_2 = models.CharField(blank=True, max_length=70)
    # satellite reference data
    satellite_ref = models.OneToOneField(SatelliteInstance, on_delete=models.CASCADE, null=True)
    user_ref = models.OneToOneField(UserInstance, on_delete=models.CASCADE, null=True)



# class MissionEventLog(models.Model):
#   mission_hash = ForeignKey(MissionInstance)
#   timestamp = models.DateTimeField()
#   message = models.CharField(blank=True, max_length=255)

admin.site.register(Satellite)
admin.site.register(MissionInstance)
admin.site.register(SatelliteInstance)
admin.site.register(UserInstance)
