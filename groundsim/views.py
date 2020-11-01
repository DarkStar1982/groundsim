import json
import julian
from hashlib import sha256
from math import floor, fmod, pi, atan, sqrt, sin, fabs, cos, atan2, trunc
from datetime import datetime, timezone, timedelta
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
from django.views.generic import View
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from groundsim.models import Satellite
from groundsim.mse.core import (
    create_mission_environment,
    create_mission_satellite,
    create_mission_instance,
    simulate_mission_steps,
    get_satellite_list,
    update_satellite,
    save_mission,
    load_mission
)

def none_is_zero(obj):
    if obj is None:
        return 0
    else:
        return obj

class SatelliteListHandler(View):
    def get(self, request):
        response = get_satellite_list()
        return HttpResponse(json.dumps(response))

@method_decorator(csrf_exempt, name='dispatch')
class UpdateSatellite(View):
    def post(self, request):
        data = request.POST.get("tle_data", None)
        update_satellite(data)
        return {"id":3, "status":"ok", "description":"satellite update succeeded"}

class InitializeHandler(View):
    def get(self, request):
        hash_id = request.GET.get("hash_id", None)
        if hash_id is not None:
            mission_instance = load_mission(hash_id)
        else:
            norad_id = int(request.GET.get("norad_id", none_is_zero(None)))
            str_date = request.GET.get("date", None)
            split_date = [int(x) for x in str_date.split(',')]
            start_date = datetime(split_date[0], split_date[1], split_date[2], split_date[3],split_date[4],split_date[5])
            mission_instance = create_mission_instance(norad_id,start_date)
        return HttpResponse(json.dumps({"status":"ok", "mission_instance":mission_instance}))

@method_decorator(csrf_exempt, name='dispatch')
class SimulationController(View):
    def post(self, request):
        step_seconds = int(request.GET.get("steps", none_is_zero(None)))
        mission_instance = json.loads(request.POST.get("mission_instance"))
        if mission_instance is None:
            return HttpResponse(json.dumps("Satellite mission not initialized"))
        else:
            mission_instance = simulate_mission_steps(mission_instance, step_seconds)
        return HttpResponse(json.dumps({"status":"ok", "mission_instance":mission_instance}))

@method_decorator(csrf_exempt, name='dispatch')
class ResetController(View):
    def post(self, request):
        mission_instance = json.loads(request.POST.get("mission_instance"))
        if mission_instance is None:
            return HttpResponse(json.dumps("Satellite mission not initialized"))
        else:
            norad_id = mission_instance["environment"]["norad_id"]
            start_date = datetime(
                mission_instance["environment"]["start_date"]["year"],
                mission_instance["environment"]["start_date"]["month"],
                mission_instance["environment"]["start_date"]["day"],
                mission_instance["environment"]["start_date"]["hour"],
                mission_instance["environment"]["start_date"]["min"],
                mission_instance["environment"]["start_date"]["sec"]
            )
            mission_instance = create_mission_instance(norad_id, start_date)
        return HttpResponse(json.dumps({"status":"ok", "mission_instance":mission_instance}))

@method_decorator(csrf_exempt, name='dispatch')
class SaveController(View):
    def post(self, request):
        mission_instance_str = request.POST.get("mission_instance",None)
        user = request.POST.get("user", None)
        email = request.POST.get("email", None)
        if mission_instance_str is None:
            return HttpResponse(json.dumps("Satellite mission data not found"))
        else:
            mission_instance = json.loads(mission_instance_str)
            hash_id = sha256(mission_instance_str.encode('utf-8')).hexdigest()
            result_data = save_mission(mission_instance, hash_id, user, email)
        return HttpResponse(json.dumps(result_data))
