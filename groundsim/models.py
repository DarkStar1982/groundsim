from django.db import models
from django.contrib import admin


class Satellite(models.Model):
    # TLE fields - line 1
    satellite_number = models.IntegerField(primary_key=True)
    satellite_name = models.CharField(max_length=24)
    satellite_class = models.CharField(max_length=1)
    launch_year = models.IntegerField()
    launch_count = models.IntegerField()
    launch_item = models.CharField(max_length=1)
    epoch_year = models.IntegerField()
    epoch_date = models.FloatField()
    mean_motion_first_derivative = models.FloatField()
    mean_motion_second_derivative = models.FloatField()
    drag_term = models.FloatField()
    tle_set_number = models.IntegerField(default=0)
    # TLE fields - line 2
    inclination = models.FloatField()
    ra_ascending_node = models.FloatField()
    eccentricty = models.FloatField()
    argument_of_perigee = models.FloatField()
    mean_anomaly = models.FloatField()
    mean_motion = models.FloatField()
    revolutions_count = models.IntegerField()
    # Subsystem fields - TBD

admin.site.register(Satellite)
