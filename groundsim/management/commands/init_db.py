from django.core.management.base import BaseCommand, CommandError
from groundsim.models import Satellite

satellite_records = [
    {
        "satellite_name":"USA224",
        "norad_id":37348,
        "tle_line1":"1 37348U 11002A   20053.50800700  .00010600  00000-0  95354-4 0 9",
        "tle_line2":"2 37348 097.9000 166.7120 0540467 271.5258 235.8003 14.76330431000000"
    },
    {
        "satellite_name":"ISS (ZARYA)",
        "norad_id":25544,
        "tle_line1":"1 25544U 98067A   20346.69133963  .00001710  00000-0  38948-4 0  9990",
        "tle_line2":"2 25544  51.6436 190.1749 0002049 117.8257 357.3518 15.49178451259535"
    }
]
def flush_db():
    Satellite.objects.all().delete()

def repopulate_db():
    for item in satellite_records:
        try:
            sat = Satellite.objects.get(norad_id=item["norad_id"])
        except Satellite.DoesNotExist:
            sat = Satellite()
        sat.norad_id = item["norad_id"]
        sat.satellite_name = item["satellite_name"]
        sat.satellite_tle1 = item["tle_line1"]
        sat.satellite_tle2 = item["tle_line2"]
        sat.save()

class Command(BaseCommand):
    help = 'Clear database and repopulate it with default data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Clearing database...'))
        flush_db()
        self.stdout.write(self.style.SUCCESS('Repopulating database...'))
        repopulate_db()
        self.stdout.write(self.style.SUCCESS('Successfully reinitialized database!'))
