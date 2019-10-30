import json
import julian
from math import floor, fmod, pi, atan, sqrt, sin, fabs, cos, atan2, trunc
from datetime import datetime
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
from django.views.generic import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from groundsim.models import Satellite

def convert_to_float(element):
    if element[0] == '-':
        sign = '-'
        mantissa = element[1:5]
        exponent = element[-1]
    else:
        sign = ''
        mantissa = element[0:4]
        exponent = element[-1]
    value = sign + '0.'+ mantissa +'E-' + exponent
    return float(value)

def parse_tle_lines(tle_line_1, tle_line_2):
    tle_data = {}
    line_1 = [x for x in tle_line_1.split(' ') if len(x)>0]
    line_2 = [x for x in tle_line_2.split(' ') if len(x)>0]
    tle_data["catalog_number"] = int(line_1[1][:-1])
    tle_data["classification"] = line_1[1][-1]
    tle_data["launch_label"] = line_1[2]
    tle_data["epoch_date"] = line_1[3]
    tle_data["first_derivative"] = float(line_1[4])
    tle_data["second_derivative"] = convert_to_float(line_1[5])
    tle_data["drag_term"] = convert_to_float(line_1[6])
    tle_data["ephemeris_type"] = int(line_1[7])
    tle_data["element_set_type"] = int(line_1[8])
    tle_data["inclination"] = float(line_2[2])
    tle_data["ra_ascending_node"] = float(line_2[3])
    tle_data["eccentricity"] = float('0.'+line_2[4])
    tle_data["argument_perigee"] = float(line_2[5])
    tle_data["mean_anomaly"] = float(line_2[6])
    tle_data["mean_motion"] = float(line_2[7])
    tle_data["revolution_number"] = int(line_2[8][:-1]) #<--bug here
    return tle_data

def convert_to_geodetic(tle_data, position, date):
    geo_data = {}
    # copy the data from SGP4 output
    x = position[0]
    y = position[1]
    z = position[2]

    # longitude calculation
    jd = julian.to_jd(date)
    ut = fmod(jd + 0.5, 1.0)
    t = (jd - ut - 2451545.0) / 36525.0
    omega = 1.0 + 8640184.812866 / 3155760000.0;
    gmst0 = 24110.54841 + t * (8640184.812866 + t * (0.093104 - t * 6.2E-6))
    theta_GMST = fmod(gmst0 + 86400* omega * ut, 86400) * 2 * pi / 86400
    lon = atan2(y,x)-theta_GMST
    lon = lon*180/pi
    geo_data["lon"] = lon
    if lon<-180:
        geo_data["lon"] = 360 + lon
    if lon>-180:
        geo_data["lon"] = lon

    # latitude calculation
    lat = atan(z/sqrt(x*x + y*y))
    a = 6378.137
    e = 0.081819190842622
    delta = 1.0
    while (delta>0.001):
        lat0 = lat
        c = (a * e * e * sin(lat0))/sqrt(1.0 - e * e * sin(lat0) * sin(lat0))
        lat = atan((z + c)/sqrt(x*x + y*y))
        delta = fabs(lat - lat0)
    geo_data["lat"] = 180*lat/pi

    #altitude calculation
    alt = sqrt(x*x + y*y)/ cos(lat) - a/sqrt(1.0 - e * e * sin(lat) * sin(lat))
    geo_data["alt"] = fabs(alt)
    return geo_data

def compute_orbit(sat_name, date):
    if date == None:
        date = datetime.now()
        formatted = [date.year, date.month, date.day, date.hour, date.minute, date.second]
    else:
        formatted = [int(x) for x in date.split(',')]
    satellite = Satellite.objects.get(satellite_name="ISS (ZARYA)")
    satellite_tle = twoline2rv(satellite.satellite_tle1, satellite.satellite_tle2, wgs72)
    tle_data_details = parse_tle_lines(satellite.satellite_tle1, satellite.satellite_tle2)

    position, velocity = satellite_tle.propagate(formatted[0], formatted[1], formatted[2], formatted[3], formatted[4], formatted[5])
    geo_data = convert_to_geodetic(tle_data_details, position, date)
    geo_data["units"] = "km"
    geo_data["id"] = str(tle_data_details["catalog_number"]) + tle_data_details["classification"]
    return geo_data

def update_satellite_tle(tle_strings):
    sat = Satellite()
    # update
    sat.satellite_name = tle_strings[0]
    sat.satellite_tle1 = tle_strings[1]
    sat.satellite_tle2 = tle_strings[2]
    sat.save()

def parse_tle_data(p_data):
    tle_lines = p_data.splitlines()
    update_satellite_tle(tle_lines)
    return split_data

def process_get(request):
    req_type = request.GET.get("command", None)
    if req_type == None:
        return {"id":0, "status":"failed", "description":"no data parameter specified"}
    else:
        if req_type == "compute_orbit":
            name = request.GET.get("sat_name", None)
            date = request.GET.get("date", None)
            return compute_orbit(name, date)
        return {"id":2, "status":"failed", "description":"unknown data parameter specified"}

def process_post(request):
    cmd_type = request.POST.get("command", None)
    if cmd_type == None:
        return {"id":3, "status":"failed", "description":"no command specified"}
    else:
        if cmd_type == "command_set_tle":
            data = request.POST.get("tle_data", None)
            return parse_tle_data(data)
    return {"id":5, "status":"failed", "description":"unknown command specified"}

@method_decorator(csrf_exempt, name='dispatch')
class ApiHandler(View):
    def get(self, request):
        response = process_get(request)
        return HttpResponse(json.dumps(response))

    def post(self, request):
        response = process_post(request)
        return HttpResponse(json.dumps(response))
