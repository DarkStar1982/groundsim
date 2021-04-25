from django.core.management.base import BaseCommand, CommandError
from groundsim.models import Satellite, SatelliteOrbitTrack
from datetime import datetime, timedelta
from groundsim.mse.lib_astro import compute_orbit_track
from groundsim.mse.lib_utils import mission_timer_to_datetime

#for each satellite in DB
# select last starting date
# check if null or not
# if null then start from today
# else start from it (need TLE epoch?)
def propagate_orbits(p_days, p_step):
    satellites = Satellite.objects.all()
    for sat in satellites:
        tle_data = {
            "line_1":sat.satellite_tle1,
            "line_2":sat.satellite_tle2,
        }
        try:
            orbit_track_latest = SatelliteOrbitTrack.objects.get(satellite_ref=sat).order_by('timestamp')[0]
            start_date = orbit_track_latest.timestamp
            start_date = start_date + timedelta(seconds = p_step)
        except SatelliteOrbitTrack.DoesNotExist:
            start_date = datetime.now()
        end_date = start_date + timedelta(days = p_days)
        track = compute_orbit_track(tle_data,mission_timer_to_datetime(start_date),mission_timer_to_datetime(end_date,p_step))
        print(track)
        #print(start_date)
        #print(end_date)



class Command(BaseCommand):
    help = 'Propagate active satellite orbits for X number of days'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Started orbit propagation calculation...'))
        propagate_orbits(1, 5)
        self.stdout.write(self.style.SUCCESS('Finished orbit propagation calculation!'))
