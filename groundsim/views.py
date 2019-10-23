import json
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from django.views.generic import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from groundsim.models import Satellite

line1 = ('1 00005U 58002B   00179.78495062  .00000023  00000-0  28098-4 0  4753')
line2 = ('2 00005  34.2682 348.7242 1859667 331.7664  19.3264 10.82419157413667')


def compute_orbit():
    satellite = twoline2rv(line1, line2, wgs72)
    position, velocity = satellite.propagate(2000, 6, 29, 12, 50, 19)
    print(satellite.error)    # nonzero on error
    print(satellite.error_message)
    print(position)
    print(velocity)

def process_get(request):
    req_type = request.GET.get("type", None)
    if req_type == None:
        return {"id":0, "status":"failed", "description":"no data parameter specified"}
    else:
        if req_type == "test":
            compute_orbit()
            return {"id":1, "value":0.0, "units":"sec","status":"ok", "description":"unknown data parameter specified"}
        return {"id":2, "status":"failed", "description":"unknown data parameter specified"}

def process_post(request):
    cmd_type = request.POST.get("command", None)
    if cmd_type == None:
        return {"id":3, "status":"failed", "description":"no command specified"}
    else:
        if cmd_type == "get_sim_status":
            return {"id":4, "status":"ok", "description":"I am fine!"}
        return {"id":5, "status":"failed", "description":"unknown command specified"}

@method_decorator(csrf_exempt, name='dispatch')
class ApiHandler(View):
    def get(self, request):
        response = process_get(request)
        return HttpResponse(json.dumps(response))

    def post(self, request):
        response = process_post(request)
        return HttpResponse(json.dumps(response))
