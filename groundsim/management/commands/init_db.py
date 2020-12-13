import json
from django.core.management.base import BaseCommand, CommandError
from groundsim.models import Satellite, MissionScenario
from groundsim.mse.utils import mission_timer_to_datetime

SATELLITE_LIST = [
    {
        "satellite_name": "OPS_SAT",
        "norad_id": 44878,
        "tle_line1": "1 44878U 19092F   20347.75591930  .00001861  00000-0  10031-3 0  9991",
        "tle_line2": "2 44878  97.4680 168.0928 0015493  97.4582 262.8412 15.15936042 54547"
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
        self.stdout.write(self.style.SUCCESS('Started reinitiliazing database...'))
        flush_db()
        repopulate_db()
        self.stdout.write(self.style.SUCCESS('Successfully reinitialized database!'))
