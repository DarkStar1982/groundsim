# mission simulation environment:
# environment simulator + satellite system simulator
import julian
from math import floor, fmod, pi, atan, sqrt, sin, fabs, cos, atan2, trunc
from datetime import datetime, timezone, timedelta
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
from groundsim.models import Satellite


###############################
#### HELPER FUNCTIONS CODE ####
###############################

def get_epoch_time(tle_string):
    year = int(tle_string[0:2])
    if year<57:
        year = 2000 + year
    else:
        year = 1957 + year
    days =  float(tle_string[2:])
    date_a = datetime(year, 1, 1,tzinfo=timezone.utc) + timedelta(days - 1)
    return date_a

# floating point comparison
def f_equals(a,b,c):
    if fabs(fabs(a)-fabs(c))<c:
        return True
    else:
        return False

def none_is_zero(obj):
    if obj is None:
        return 0
    else:
        return obj

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

#update or insert
def update_satellite(p_data):
    tle_lines = p_data.splitlines()
    object_data = parse_tle_lines(tle_lines[1], tle_lines[2])
    sat = None
    norad_id = object_data["catalog_number"]
    try:
        sat = Satellite.objects.get(norad_id=norad_id)
    except Satellite.DoesNotExist:
        sat = Satellite()
    sat.satellite_name = tle_lines[0]
    sat.satellite_tle1 = tle_lines[1]
    sat.satellite_tle2 = tle_lines[2]
    sat.norad_id = norad_id
    sat.save()

def get_satellite_list():
    resp_sats = {}
    sat_list = []
    satellites= Satellite.objects.all()
    for item in satellites:
        sat_list.append({"sat_name":item.satellite_name, "norad_id":item.norad_id})
    resp_sats["status"] = "ok"
    resp_sats["satelites"] = sat_list
    return resp_sats

def parse_tle_lines(tle_line_1, tle_line_2):
    tle_data = {}
    line_1 = [x for x in tle_line_1.split(' ') if len(x)>0]
    # insert whitespace separator to correctly process last two elements - maybe optional!
    if tle_line_2[-5] !=' ':
        line3 = tle_line_2[0:-4] + ' '+ tle_line_2[-4:]
    line_2 = [x for x in line3.split(' ') if len(x)>0]
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
    tle_data["revolution_number"] = int(line_2[8][:-1])
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
    geo_data["lng"] = lon
    if lon<-180:
        geo_data["lng"] = 360 + lon
    if lon>-180:
        geo_data["lng"] = lon

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
    if f_equals(lat,pi/2,0.01):
        alt = z/sin(lat) - a*sqrt(1-e*e)
    else:
        alt = sqrt(x*x + y*y)/ cos(lat) - a/sqrt(1.0 - e * e * sin(lat) * sin(lat))
    geo_data["alt"] = fabs(alt)
    #geo_data["a"] = a + geo_data["alt"]
    return geo_data

def generate_tle_data(norad_id):
    satellite_record = Satellite.objects.get(norad_id=norad_id)
    #satellite_object = twoline2rv(satellite_record.satellite_tle1, satellite_record.satellite_tle2, wgs72)
    #tle_object = parse_tle_lines(satellite_record.satellite_tle1, satellite_record.satellite_tle2)
    return { "line_1":satellite_record.satellite_tle1, "line_2":satellite_record.satellite_tle2 }

#####################################
#### ENVIRONMENT SIMULATION CODE ####
#####################################
def create_mission_environment(p_norad_id, p_start_date):
    environment = {}
    environment["norad_id"] = p_norad_id
    #environment["start_date_packed"] = p_start_date <-not JSONable
    environment["mission_timer"] = {
        "year": p_start_date.year,
        "month":p_start_date.month,
        "day":  p_start_date.day,
        "hour": p_start_date.hour,
        "min":  p_start_date.minute,
        "sec":  p_start_date.second
    }
    environment["tle_data"] = generate_tle_data(p_norad_id)
    environment["elapsed_timer"] = 0
    environment["ground_track"] = None
    environment["orbit_vector"] = None
    environment["sun_vector"] = None
    environment["ground_stations"] = []
    return environment

def increment_mission_timer(mission_timer, p_seconds):
    # TODO
    return mission_timer

def propagate_orbit(tle_data, mission_timer):
    satellite_object = twoline2rv(tle_data["line_1"], tle_data["line_2"], wgs72)
    position, velocity = satellite_object.propagate(
        mission_timer["year"],
        mission_timer["month"],
        mission_timer["day"],
        mission_timer["hour"],
        mission_timer["min"],
        mission_timer["sec"]
    )
    return {"orbit_position": position, "orbit_velocity":velocity}

def get_ground_track(tle_data, orbital_vector, p_date):
    current_date = datetime(p_date["year"], p_date["month"], p_date["day"], p_date["hour"],p_date["min"],p_date["sec"])
    tle_object = parse_tle_lines(tle_data["line_1"], tle_data["line_2"])
    ground_track = convert_to_geodetic(tle_object, orbital_vector["orbit_position"], current_date)
    return ground_track

# at 1 second resolution
def evolve_environment(p_environment, p_seconds):
    p_environment["elapsed_timer"] = p_environment["elapsed_timer"] + p_seconds
    p_environment["mission_timer"] = increment_mission_timer(p_environment["mission_timer"], p_seconds)
    p_environment["orbit_vector"] = propagate_orbit(p_environment["tle_data"], p_environment["mission_timer"])
    p_environment["ground_track"] = get_ground_track(p_environment["tle_data"], p_environment["orbit_vector"], p_environment["mission_timer"])
    return p_environment


################################################################################
########################## SATELLITE SIMULATION CODE ###########################
################################################################################
def create_mission_satellite():
    satellite = {}
    return satellite

# at 1 second resolution - input is Environment simulation output
def evolve_satellite(p_satellite, p_seconds):
    return p_satellite

def get_log():
    return {"status":"ok", "page":0, "log":[]}

def get_instruments_status():
    return {"status":"ok", "page":0, "instruments":[]}

def get_telemetry(norad_id):
    return {
        "status":"ok",
        "power":[
            {"param":"param","value":"value"},
            {"param":"param2","value":"value2"},
            {"param":"param3","value":"value3"},
            {"param":"param4","value":"value4"}
        ],
        "thermal":[
            {"param":"param","value":"value"},
            {"param":"param2","value":"value2"},
            {"param":"param3","value":"value3"},
            {"param":"param4","value":"value4"}
        ],
        "obdh":[
            {"param":"param","value":"value"},
            {"param":"param2","value":"value2"},
            {"param":"param3","value":"value3"},
            {"param":"param4","value":"value4"}
        ],
        "adcs":[
            {"param":"param","value":"value"},
            {"param":"param2","value":"value2"},
            {"param":"param3","value":"value3"},
            {"param":"param4","value":"value4"}
        ]
    }

# should include ground station visibility calculation
def queue_command():
    pass

#################################
#### MISSION SIMULATION CODE ####
#################################
def create_mission_instance(p_environment, p_satellite):
    mission = {}
    mission["environment"] = p_environment
    mission["satellite"] = p_satellite
    return mission

def simulate_mission_steps(p_mission, p_seconds):
    p_mission["environment"] = evolve_environment(p_mission["environment"], p_seconds)
    p_mission["satellite"] = evolve_satellite(p_mission["satellite"], p_seconds)
    return p_mission
