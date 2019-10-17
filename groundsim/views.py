import json
from django.views.generic import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def process_data_request(req_type):
    if req_type == None:
        return {"id":0, "status":"failed", "description":"no data parameter specified"}
    else:
        if req_type == "test":
            return {"id":1, "value":0.0, "units":"sec","status":"ok", "description":"unknown data parameter specified"}
        return {"id":2, "status":"failed", "description":"unknown data parameter specified"}

def process_command(cmd_type):
    if cmd_type == None:
        return {"id":3, "status":"failed", "description":"no command specified"}
    else:
        if cmd_type == "get_sim_status":
            return {"id":4, "status":"ok", "description":"I am fine!"}
        return {"id":5, "status":"failed", "description":"unknown command specified"}

@method_decorator(csrf_exempt, name='dispatch')
class ApiHandler(View):
    def get(self, request):
        request_type = request.GET.get("type", None)
        data_response = process_data_request(request_type)
        return HttpResponse(json.dumps(data_response))

    def post(self, request):
        cmd = request.POST.get("command", None)
        command_response = process_command(cmd)
        return HttpResponse(json.dumps(command_response))
