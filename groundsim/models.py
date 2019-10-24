from django.db import models
from django.contrib import admin


class Satellite(models.Model):
    satellite_name = models.CharField(max_length=24) # tle line 0
    satellite_tle1 = models.CharField(max_length=70)
    satellite_tle2 = models.CharField(max_length=70)
    # Subsystem fields - TBD

admin.site.register(Satellite)
