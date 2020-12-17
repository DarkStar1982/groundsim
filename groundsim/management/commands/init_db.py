import json
from django.core.management.base import BaseCommand, CommandError
from groundsim.models import Satellite, MissionScenario
from groundsim.mse.core_utils import mission_timer_to_datetime

SATELLITE_LIST = [
    {
        "satellite_name": "OPS_SAT",
        "norad_id": 44878,
        "tle_line1": "1 44878U 19092F   20351.51834954  .00001625  00000-0  87961-4 0  9991",
        "tle_line2": "2 44878  97.4685 171.7951 0015492  85.6297 274.6705 15.15948331 55114",
        "config_instrument": {
            "imager": {
                "fov":2.22,
                "d":0.0225,
                "f":0.58,
                "sensor":[4096,4096],
                "pixel":5.5E-6
            },
        }
    },
    {
        "satellite_name": "COSMOS_2545",
        "norad_id": 45358,
        "tle_line1": "1 45358U 20018A   20347.66636832 -.00000045  00000-0  00000+0 0  9991",
        "tle_line2": "2 45358  64.8695  22.4196 0011468 249.4798 186.1892  2.13102640  577",
        "config_instrument": {
            "imager": {
                "fov":1.6,
                "d":0.01,
                "f":0.5,
                "sensor":[4096,3072],
                "pixel":3.2E-6
            },
        }
    }
]

MISSION_SCENARIOS = [
    {
        "scenario_id":1,
        "start_date":{
            "year":2020,
            "month":11,
            "day": 28,
            "hour":20,
            "min": 26,
            "sec": 16
        },
        "mission_name": "eo_basic",
        "description": "A basic Earth Observation mission",
        "initial_setup":{
            "norad_id":44878,
            "fp_precision":0.001
        },
        "objectives":[
            {
                "type":"take_photo",
                "score_points":100,
                "definition":{
                    "top": 26.327,
                    "left": -38.374,
                    "bottom":26.198,
                    "right":-38.231,
                    "target":"Earth"
                }
            }
        ],
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
        sat.config_instrument = json.dumps(item["config_instrument"])
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
        self.stdout.write(self.style.SUCCESS('Started reinitiliazing database...'))
        flush_db()
        repopulate_db()
        self.stdout.write(self.style.SUCCESS('Successfully reinitialized database!'))
