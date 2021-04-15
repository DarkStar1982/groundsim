import json
from django.views.generic import View
from django.http import HttpResponse, HttpResponseNotFound

class NovaInstrumentListController(View):
    def get(self, request):
        result_data = ["INSTRUMENT LIST - OK"]
        return HttpResponse(json.dumps(result_data))

class NovaSchedulerController(View):
    def get(self, request):
        result_data = ["SCHEDULER - OK"]
        return HttpResponse(json.dumps(result_data))

class NovaImagerController(View):
    def get(self, request):
        result_data = ["IMAGER - OK"]
        return HttpResponse(json.dumps(result_data))

class NovaDownloadController(View):
    def get(self, request):
        result_data = ["DOWNLOAD - OK"]
        return HttpResponse(json.dumps(result_data))
