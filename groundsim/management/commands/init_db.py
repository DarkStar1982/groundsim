import json
from django.core.management.base import BaseCommand, CommandError
from groundsim.models import Satellite, MissionScenario
from groundsim.mse.utils import mission_timer_to_datetime

SATELLITE_LIST = [
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

MISSION_SCENARIOS = [
    {
        "scenario_id":1,
        "start_date":{
            "year":2020,
            "month":11,
            "day":4,
            "hour":18,
            "min":40,
            "sec": 37
        },
        "mission_name": "eo_basic",
        "description": "A basic Earth Observation mission",
        "initial_setup":{
            "norad_id":25544,
            "fp_precision":0.001
        },
        "objectives":[
            {
                "type":"take_photo",
                "score_points":100,
                "definition":{
                    "top": 46.255,
                    "left": 30.243,
                    "bottom":46.129,
                    "right":30.423,
                    "target":"Earth"
                }
            }
        ]
    }
]

def flush_db():
    Satellite.objects.all().delete()
    MissionScenario.objects.all().delete()

def repopulate_db():
    # add satellites
    for item in SATELLITE_LIST:
        try:
            sat = Satellite.objects.get(norad_id=item["norad_id"])
        except Satellite.DoesNotExist:
            sat = Satellite()
        sat.norad_id = item["norad_id"]
        sat.satellite_name = item["satellite_name"]
        sat.satellite_tle1 = item["tle_line1"]
        sat.satellite_tle2 = item["tle_line2"]
        sat.save()
    # add missions
    for item in MISSION_SCENARIOS:
        try:
            scenario = MissionScenario.objects.get(scenario_id=item["scenario_id"])
        except MissionScenario.DoesNotExist:
            scenario = MissionScenario()
        scenario.scenario_id =item["scenario_id"]
        scenario.start_date = mission_timer_to_datetime(item["start_date"])
        scenario.mission_name = item["mission_name"]
        scenario.description = item["description"]
        scenario.initial_setup = json.dumps(item["initial_setup"])
        scenario.objectives = json.dumps(item["objectives"])
        scenario.save()


class Command(BaseCommand):
    help = 'Clear database and repopulate it with default data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Started reinitiliazing database with...'))
        flush_db()
        repopulate_db()
        self.stdout.write(self.style.SUCCESS('Successfully reinitialized database!'))
