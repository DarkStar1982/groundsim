# mission simulation environment:
# environment simulator + satellite system simulator
import julian
import calendar
from math import floor, fmod, pi, tan, atan, sqrt, sin, fabs, cos, atan2, trunc, acos
from datetime import datetime, timezone, timedelta
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
from groundsim.models import Satellite

################################################################################
############################### GLOBAL CONSTANTS ###############################
################################################################################

R_EARTH = 6378.137 # in km
J2 = 1.08E-3 # second harmonic
MU_EARTH = 3.986E14
# day duration
SIDEREAL_DAY = 86164.0905
UTC_DAY = 86400

################################################################################
############################# HELPER FUNCTIONS CODE ############################
################################################################################

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
        sat_list.append(
            {"sat_name":item.satellite_name,
            "norad_id":item.norad_id}
        )
    resp_sats["status"] = "ok"
    resp_sats["satelites"] = sat_list
    return resp_sats

def generate_tle_data(norad_id):
    satellite_record = Satellite.objects.get(norad_id=norad_id)
    return {
        "line_1":satellite_record.satellite_tle1,
        "line_2":satellite_record.satellite_tle2
    }

def parse_tle_lines(tle_line_1, tle_line_2):
    tle_data = {}
    line_1 = [x for x in tle_line_1.split(' ') if len(x)>0]
    # insert whitespace to correctly process last two elements - maybe optional!
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


def calculate_camera_fov(d,f):
    alpha = 2*atan(d/(2*f))
    return alpha

def calculate_resolution(ifov, alt):
    d = 2*alt*tan(ifov/2)
    return d

# lat lon should be in radians
def calculate_degree_len(lat):
    # calculate latitude degree length
    length_lat = (111132.954 - 559.822 * cos(2*lat)+1.175 * cos(4*lat))/1000.0
    length_lon = (pi * R_EARTH * cos (lat))/180
    return {"length_lon":length_lon, "length_lat":length_lat}

################################################################################
########################## ENVIRONMENT SIMULATION CODE #########################
################################################################################
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

def increment_mission_timer(p_mission_timer, p_seconds):
    # date_start = convert mission timer to datetime
    current_date = datetime(
        p_mission_timer["year"],
        p_mission_timer["month"],
        p_mission_timer["day"],
        p_mission_timer["hour"],
        p_mission_timer["min"],
        p_mission_timer["sec"]
    )
    # add delta in seconds
    delta = timedelta(seconds=p_seconds)
    new_date = current_date + delta
    # convert back to expanded view
    p_mission_timer["year"] = new_date.year
    p_mission_timer["month"] = new_date.month
    p_mission_timer["day"] = new_date.day
    p_mission_timer["hour"] = new_date.hour
    p_mission_timer["min"] = new_date.minute
    p_mission_timer["sec"] = new_date.second
    return p_mission_timer

def mission_timer_to_str(p_mission_timer):
    str_timer = "%02i:%02i:%02i, %02i %s %s" % (
        p_mission_timer["hour"],
        p_mission_timer["min"],
        p_mission_timer["sec"],
        p_mission_timer["day"],
        calendar.month_abbr[p_mission_timer["month"]],
        p_mission_timer["year"],
    )
    return str_timer

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
    a = R_EARTH
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
        alt = sqrt(x*x + y*y)/cos(lat) - a/sqrt(1.0 - e*e*sin(lat)*sin(lat))
    geo_data["alt"] = fabs(alt)
    return geo_data

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
    current_date = datetime(
        p_date["year"],
        p_date["month"],
        p_date["day"],
        p_date["hour"],
        p_date["min"],
        p_date["sec"]
    )
    tle_object = parse_tle_lines(tle_data["line_1"], tle_data["line_2"])
    ground_track = convert_to_geodetic(
        tle_object,
        orbital_vector["orbit_position"],
        current_date
    )
    return ground_track

# time since periapsis calculation - all wrong!
# FIXME!
def time_since_periapsis(position_object, mean_motion):
    radius = (position_object["alt"] + R_EARTH)*1000
    orbital_period = 86400/mean_motion
    eccentricity = position_object["e"]
    semimajor_axis = ((pow(orbital_period,2)*MU_EARTH)/(4*pow(pi,2)))**(1.0/3.0)
    eccentric_anomaly = acos((1 - radius/semimajor_axis)/eccentricity)
    mean_anomaly = eccentric_anomaly - eccentricity*sin(eccentric_anomaly)
    time_since_periapsis = mean_anomaly/(2*pi) * orbital_period
    return time_since_periapsis

# at 1 second resolution
def evolve_environment(p_environment, p_seconds):
    p_environment["elapsed_timer"] = p_environment["elapsed_timer"] + p_seconds
    p_environment["mission_timer"] = increment_mission_timer(
        p_environment["mission_timer"],
        p_seconds
    )
    p_environment["orbit_vector"] = propagate_orbit(
        p_environment["tle_data"],
        p_environment["mission_timer"]
    )
    p_environment["ground_track"] = get_ground_track(
        p_environment["tle_data"],
        p_environment["orbit_vector"],
        p_environment["mission_timer"]
    )
    return p_environment


################################################################################
########################## SATELLITE SIMULATION CODE ###########################
################################################################################

def initialize_satellite_geometry():
    sat_geometry = {}
    return sat_geometry

def initialize_satellite_subsystems():
    sat_components = {
        "power": {
            "solar_panels": {},
            "battery":{},
            "pdu":{},
            "power_bus":{}
        },
        "adcs": {
            "imu" :{},
            "gyro_x":{},
            "gyro_y":{},
        },
        "obdh": {
            "cpu": {},
            "ram": {},
            "storage":{},
            "data_bus":{}
        },
        "comm":{
            "receiver":{},
            "transmitter":{},
            "data_bus":{}
        }
    }
    return sat_components

def initialize_satellite_telemetry():
    telemetry = {
        "power": {
            "battery_level":100.0,
            "battery_input":0.0,
            "battery_output":0.0,
            "solar_panel_output":0.0
        },
        "adcs": {
            "gyro_rpm":0,
            "attitude_mode": "SUN_POINTING",
            "adcs_status": "OK",
            "adcs_vectors":[]
        },
        "obdh": {
            "obdh_status":"OK",
            "cpu_load": 0.0,
            "storage_capacity":100.0,
            "tasks_running":[]
        },
        "thermal": {
            "chassis_temp": 0.0,
            "solar_panel_temp":0.0,
            "obdh_board_temp":0.0,
            "battery_temp":0.0
        }
    }
    return telemetry

def initialize_satellite_instruments():
    instruments = {
        "imager": {
            "fov":0.03874630939427412,
            "f":0.58,
            "sensor":[4096,3072],
            "pixel":5.5E-6
        },
        "sdr": {}
    }

    return instruments

def create_mission_satellite():
    # should be configurable
    satellite = {
        "geometry":{},
        "subsystems":{},
        "instruments":{},
        "telemetry":{},
    }

    # load from DB - TBD

    satellite["geometry"] = initialize_satellite_geometry()
    # initialize satellite subsystems
    satellite["subsystems"] = initialize_satellite_subsystems()
    # initialize telemetry parameters
    satellite["telemetry"] = initialize_satellite_telemetry()
    # initialize satellite instruments
    satellite["instruments"] = initialize_satellite_instruments()
    return satellite

def get_log():
    return {"status":"ok", "page":0, "log":[]}

def get_instruments_status():
    return {"status":"ok", "page":0, "instruments":[]}

# should include ground station visibility calculation
def queue_commands():
    pass

# input:
# - camera fov drawing
#  |\
#  | \
# a|  \ c
#  |   \
#  -----
#     b
def get_imager_frame(p_mission):
    fov_angle = p_mission["satellite"]["instruments"]["imager"]["fov"]
    altitude = p_mission["environment"]["ground_track"]["alt"]
    lat = pi*p_mission["environment"]["ground_track"]["lat"]/180
    swath=2*altitude*tan(fov_angle/2.0)
    deg_length = calculate_degree_len(lat)
    result = {
        "swath":swath,
        "swath_lat":swath/deg_length["length_lat"],
        "swath_lon":swath/deg_length["length_lon"],
    }
    return result

# at 1 second resolution - input is Environment, output is new satellite
def evolve_satellite(p_satellite, p_environemnt, p_seconds):
    return p_satellite

################################################################################
############################ MISSION SIMULATION API ############################
################################################################################
def create_mission_instance(p_environment, p_satellite):
    mission = {}
    mission["environment"] = p_environment
    mission["satellite"] = p_satellite
    return mission

def simulate_mission_steps(p_mission, steps):
    p_mission["environment"] = evolve_environment(p_mission["environment"], steps)
    p_mission["satellite"] = evolve_satellite(p_mission["satellite"], p_mission["environment"], steps)
    return p_mission

def get_satellite_position(p_mission):
    position_object = {}
    tle_details = parse_tle_lines(
        p_mission["environment"]["tle_data"]["line_1"],
        p_mission["environment"]["tle_data"]["line_2"]
    )
    position_object["lat"] = p_mission["environment"]["ground_track"]["lat"]
    position_object["lng"] = p_mission["environment"]["ground_track"]["lng"]
    position_object["alt"] = p_mission["environment"]["ground_track"]["alt"]
    # position_object["a"] = TBD
    position_object["e"] = tle_details["eccentricity"]
    position_object["i"] = tle_details["inclination"]
    position_object["ra"] = tle_details["ra_ascending_node"]
    position_object["w"] = tle_details["argument_perigee"]
    position_object["time"] = mission_timer_to_str(p_mission["environment"]["mission_timer"])
    position_object["status"] = "OK"
    position_object["tp"] = time_since_periapsis(position_object, tle_details["mean_motion"])
    return position_object

def get_satellite_telemetry(p_mission):
    telemetry_object =  {
        "status":"ok",
        "power": {
            "battery_level": p_mission["satellite"]["telemetry"]["power"]["battery_level"],
            "battery_output":p_mission["satellite"]["telemetry"]["power"]["battery_output"],
            "battery_input": p_mission["satellite"]["telemetry"]["power"]["battery_input"],
            "solar_panel_output":p_mission["satellite"]["telemetry"]["power"]["solar_panel_output"],
        },
        "thermal":{
            "chassis_temp": p_mission["satellite"]["telemetry"]["thermal"]["chassis_temp"],
            "solar_panel_temp":p_mission["satellite"]["telemetry"]["thermal"]["solar_panel_temp"],
            "obdh_board_temp":p_mission["satellite"]["telemetry"]["thermal"]["obdh_board_temp"],
            "battery_temp":p_mission["satellite"]["telemetry"]["thermal"]["battery_temp"]
        },
        "obdh":{
            "obdh_status":p_mission["satellite"]["telemetry"]["obdh"]["obdh_status"],
            "cpu_load": p_mission["satellite"]["telemetry"]["obdh"]["cpu_load"],
            "storage_capacity":p_mission["satellite"]["telemetry"]["obdh"]["storage_capacity"],
            "tasks_running":p_mission["satellite"]["telemetry"]["obdh"]["tasks_running"],
        },
        "adcs":{
            "gyro_rpm":p_mission["satellite"]["telemetry"]["adcs"]["gyro_rpm"],
            "attitude_mode": p_mission["satellite"]["telemetry"]["adcs"]["attitude_mode"],
            "adcs_status":p_mission["satellite"]["telemetry"]["adcs"]["adcs_status"],
            "adcs_vectors":p_mission["satellite"]["telemetry"]["adcs"]["adcs_vectors"],
        }
    }
    return telemetry_object
