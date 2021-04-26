from django.core.management.base import BaseCommand, CommandError
from groundsim.models import Satellite, SatelliteOrbitTrack
from datetime import datetime, timedelta
from groundsim.mse.lib_astro import compute_orbit_track
from groundsim.mse.lib_utils import datetime_to_mission_timer

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
            orbit_track_latest = SatelliteOrbitTrack.objects.filter(satellite_ref=sat).order_by('-timestamp')
            if not orbit_track_latest:
                raise SatelliteOrbitTrack.DoesNotExist
            else:
                start_date = orbit_track_latest[0].timestamp
                start_date = start_date + timedelta(seconds = p_step)
        except SatelliteOrbitTrack.DoesNotExist:
            start_date = datetime.now()
        end_date = start_date + timedelta(days = p_days)
        print(start_date)
        print(end_date)
        track = compute_orbit_track(tle_data,datetime_to_mission_timer(start_date),datetime_to_mission_timer(end_date),p_step)
        for item in track:
            new_record = SatelliteOrbitTrack()
            new_record.satellite_ref = sat
            new_record.timestamp = item["timestamp"]
            new_record.latitude = item["lat"]
            new_record.longitude = item["lng"]
            new_record.altitude = item["alt"]
            new_record.save()

class Command(BaseCommand):
    help = 'Propagate active satellite orbits for X number of days'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('days', nargs='+', type=int)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Started orbit propagation calculation...'))
        days = options['days']
        start_time = datetime.now()
        propagate_orbits(days[0], 5)
        end_time = datetime.now() - start_time
        self.stdout.write(self.style.SUCCESS('Finished %s days of orbit propagation calculation in %s seconds' % (days[0],end_time.seconds)))
