# mission simulation environment:
# environment simulator + satellite system simulator
import calendar
import json
from hashlib import sha256
from math import pi, tan, atan, sqrt, sin, fabs, cos, atan2, trunc, acos
from datetime import datetime, timezone, timedelta
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
from groundsim.models import Satellite, SatelliteInstance, MissionInstance, UserInstance
from groundsim.mse.utils import time_since_periapsis, parse_tle_lines, convert_to_geodetic, calculate_degree_len

################################################################################
########################## ENVIRONMENT SIMULATION CODE #########################
################################################################################

class CMSE_Env():
    def create_mission_environment(self, p_norad_id, p_start_date):
        environment = {}
        environment["norad_id"] = p_norad_id
        environment["current_date"] = {
            "year": p_start_date.year,
            "month":p_start_date.month,
            "day":  p_start_date.day,
            "hour": p_start_date.hour,
            "min":  p_start_date.minute,
            "sec":  p_start_date.second
        }
        environment["start_date"] = environment["current_date"]
        environment["tle_data"] = self.generate_tle_data(p_norad_id)
        environment["elapsed_timer"] = 0
        environment["ground_track"] = None
        environment["orbit_vector"] = None
        environment["sun_vector"] = None
        environment["ground_stations"] = []
        environment["user"] = None
        environment["email"] = None
        environment["hash_id"] = None
        environment["mission_selected"] = None
        environment["log_buffer"] = []
        return environment

    def generate_tle_data(self, norad_id):
        satellite_record = Satellite.objects.get(norad_id=norad_id)
        return {
            "line_1":satellite_record.satellite_tle1,
            "line_2":satellite_record.satellite_tle2
        }

    def increment_mission_timer(self, p_mission_timer, p_seconds):
        # date_start = convert mission timer to datetime
        current_date = self.mission_timer_to_datetime(p_mission_timer)
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

    def mission_timer_to_str(self, p_mission_timer):
        str_timer = "%02i:%02i:%02i, %02i %s %s" % (
            p_mission_timer["hour"],
            p_mission_timer["min"],
            p_mission_timer["sec"],
            p_mission_timer["day"],
            calendar.month_abbr[p_mission_timer["month"]],
            p_mission_timer["year"],
        )
        return str_timer

    def mission_timer_to_datetime(self, p_mission_timer):
        packed_date = datetime(
            p_mission_timer["year"],
            p_mission_timer["month"],
            p_mission_timer["day"],
            p_mission_timer["hour"],
            p_mission_timer["min"],
            p_mission_timer["sec"]
        )
        return packed_date

    def propagate_orbit(self, tle_data, mission_timer):
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

    def get_ground_track(self, tle_data, orbital_vector, p_date):
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

    def log_event(self, p_environment, p_event_string):
        # save event  if mission exists in DB
        if p_environment["hash_id"] is not None:
            mission_record = MissionInstance.objects.get(mission_hash=hash_id)
            event_record = MissionEventLog()
            event_record.mission_ref = mission_record
            event_record.timestamp = self.mission_timer_to_datetime(p_environment["current_date"])
            event_record.message = p_event_string
            event_record.save()
        timestamp = self.mission_timer_to_str(p_environment["current_date"])
        p_environment["log_buffer"].append([timestamp, p_event_string])
        # keep length of the buffer at 10
        if len(p_environment["log_buffer"])>10:
            p_environment["log_buffer"].pop(0)
        return p_environment

    # at 1 second resolution
    def evolve_environment(self, p_environment, p_seconds):
        p_environment["elapsed_timer"] = p_environment["elapsed_timer"] + p_seconds
        p_environment["current_date"] = self.increment_mission_timer(
            p_environment["current_date"],
            p_seconds
        )
        p_environment["orbit_vector"] = self.propagate_orbit(
            p_environment["tle_data"],
            p_environment["current_date"]
        )
        p_environment["ground_track"] = self.get_ground_track(
            p_environment["tle_data"],
            p_environment["orbit_vector"],
            p_environment["current_date"]
        )
        event_message = "Test mission event %s" % int(p_environment["elapsed_timer"]/p_seconds)
        p_environment = self.log_event(p_environment, event_message)
        return p_environment

################################################################################
########################## SATELLITE SIMULATION CODE ###########################
################################################################################

class CMSE_Sat():
    #load physics model
    def initialize_satellite_geometry(self):
        sat_geometry = {}
        return sat_geometry

    # should be configurable or loadable from DB
    def create_mission_satellite(self):
        satellite = {
            "geometry":self.initialize_satellite_geometry(),
            "subsystems":self.initialize_satellite_subsystems(),
            "instruments":self.initialize_satellite_instruments(),
            "telemetry":self.initialize_satellite_telemetry(),
        }
        return satellite

    def initialize_satellite_subsystems(self):
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

    def initialize_satellite_instruments(self):
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

    def initialize_satellite_telemetry(self):
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

    def load_mission_satellite(self, satellite_record):
        satellite = {
            "geometry":json.loads(satellite_record.geometry),
            "subsystems":json.loads(satellite_record.subsystems),
            "instruments":json.loads(satellite_record.instruments),
            "telemetry":self.initialize_satellite_telemetry(),
        }
        return satellite

    def get_satellite_position(self, p_mission):
        position_object = {}
        tle_details = parse_tle_lines(
            p_mission["environment"]["tle_data"]["line_1"],
            p_mission["environment"]["tle_data"]["line_2"]
        )
        position_object["lat"] = p_mission["environment"]["ground_track"]["lat"]
        position_object["lng"] = p_mission["environment"]["ground_track"]["lng"]
        position_object["alt"] = p_mission["environment"]["ground_track"]["alt"]
        # value a TBD
        position_object["a"] = 0
        position_object["e"] = tle_details["eccentricity"]
        position_object["i"] = tle_details["inclination"]
        position_object["ra"] = tle_details["ra_ascending_node"]
        position_object["w"] = tle_details["argument_perigee"]
        position_object["time"] = EnvironmentSimulator.mission_timer_to_str(p_mission["environment"]["current_date"])
        position_object["status"] = "ok"
        position_object["tp"] = time_since_periapsis(position_object, tle_details["mean_motion"])
        return position_object

    # REMOVE ME - TBD
    def get_satellite_telemetry(self, p_mission):
        telemetry_object =  {
            "status":"ok",
            "power": {
                "1": {"name":"battery_level","value":p_mission["satellite"]["telemetry"]["power"]["battery_level"]},
                "2": {"name":"battery_output","value":p_mission["satellite"]["telemetry"]["power"]["battery_output"]},
                "3": {"name":"battery_input","value":p_mission["satellite"]["telemetry"]["power"]["battery_input"]},
                "4": {"name":"solar_panel_output","value":p_mission["satellite"]["telemetry"]["power"]["solar_panel_output"]},
            },
            "thermal":{
                "1": {"name":"chassis_temp","value":p_mission["satellite"]["telemetry"]["thermal"]["chassis_temp"]},
                "2": {"name":"solar_panel_temp","value":p_mission["satellite"]["telemetry"]["thermal"]["solar_panel_temp"]},
                "3": {"name":"obdh_board_temp","value":p_mission["satellite"]["telemetry"]["thermal"]["obdh_board_temp"]},
                "4": {"name":"battery_temp","value":p_mission["satellite"]["telemetry"]["thermal"]["battery_temp"]},
            },
            "obdh":{
                "1": {"name":"obdh_status","value":p_mission["satellite"]["telemetry"]["obdh"]["obdh_status"]},
                "2": {"name":"cpu_load","value":p_mission["satellite"]["telemetry"]["obdh"]["cpu_load"]},
                "3": {"name":"storage_capacity","value":p_mission["satellite"]["telemetry"]["obdh"]["storage_capacity"]},
                "4": {"name":"tasks_running","value":p_mission["satellite"]["telemetry"]["obdh"]["tasks_running"]},
            },
            "adcs":{
                "1": {"name":"gyro_rpm","value":p_mission["satellite"]["telemetry"]["adcs"]["gyro_rpm"]},
                "2": {"name":"attitude_mode","value":p_mission["satellite"]["telemetry"]["adcs"]["attitude_mode"]},
                "3": {"name":"adcs_status","value":p_mission["satellite"]["telemetry"]["adcs"]["adcs_status"]},
                "4": {"name":"adcs_vectors","value":p_mission["satellite"]["telemetry"]["adcs"]["adcs_vectors"]},
            }
        }
        return telemetry_object

    # should include ground station visibility calculation - TBD
    def process_command_script(self):
        pass

    def get_imager_frame(self, p_mission):
        fov_angle = p_mission["satellite"]["instruments"]["imager"]["fov"]
        altitude = p_mission["environment"]["ground_track"]["alt"]
        lat = pi*p_mission["environment"]["ground_track"]["lat"]/180
        lon = pi*p_mission["environment"]["ground_track"]["lng"]/180
        swath=2*altitude*tan(fov_angle/2.0)
        deg_length = calculate_degree_len(lat)
        swath_lat = swath/deg_length["length_lat"]
        swath_lon = swath/deg_length["length_lon"]
        a = p_mission["environment"]["ground_track"]["lat"] + swath_lat/2
        b = p_mission["environment"]["ground_track"]["lat"] - swath_lat/2
        c = p_mission["environment"]["ground_track"]["lng"] + swath_lon/2
        d = p_mission["environment"]["ground_track"]["lng"] - swath_lon/2
        result = {
            "top": max(a,b),
            "left": min(c,d),
            "bottom": min(a,b),
            "right":max(c,d)
        }
        return result

    # at 1 second resolution - input is Environment, output is new satellite
    def evolve_satellite(self, p_mission, p_seconds):
        p_mission["satellite"]["location"] = self.get_satellite_position(p_mission)
        p_mission["satellite"]["formatted_telemetry"] = self.get_satellite_telemetry(p_mission)
        p_mission["satellite"]["instruments"]["imager"]["frame"] = self.get_imager_frame(p_mission)
        return p_mission["satellite"]

################################################################################
############################ MISSION SIMULATION API ############################
################################################################################

# update or insert new
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

def create_mission_instance(norad_id, start_date):
    mission = {}
    mission["environment"] = EnvironmentSimulator.create_mission_environment(norad_id, start_date)
    mission["satellite"] = SatelliteSimulator.create_mission_satellite()
    return mission

def simulate_mission_steps(p_mission, steps):
    p_mission["environment"] = EnvironmentSimulator.evolve_environment(p_mission["environment"], steps)
    p_mission["satellite"] = SatelliteSimulator.evolve_satellite(p_mission, steps)
    return p_mission

def save_user(p_user, p_email):
    record, created = UserInstance.objects.get_or_create(user=p_user, email = p_email)
    return record

# check if mission record already exists before saving
def save_mission(p_mission, p_user, p_email):
    if p_mission["environment"]["user"] is None and p_mission["environment"]["email"] is None:
        hash_id = sha256(json.dumps(p_mission).encode('utf-8')).hexdigest()
        user_record = save_user(p_user, p_email)
        mission_record = MissionInstance()
        satellite_record = SatelliteInstance()
        p_mission["environment"]["user"] = p_user
        p_mission["environment"]["email"] = p_email
        p_mission["environment"]["hash_id"] = hash_id
        mission_record.mission_hash = hash_id
        mission_record.save()
        user_record.mission_ref = mission_record
        user_record.save()
    else:
        hash_id = p_mission["environment"]["hash_id"]
        mission_record = MissionInstance.objects.get(
            mission_hash=hash_id
        )
        satellite_record = mission_record.satellite_ref
        # hash_id = sha256(json.dumps(p_mission).encode('utf-8')).hexdigest()
    satellite_record.satellite_id = p_mission["environment"]["norad_id"]
    satellite_record.geometry = json.dumps(p_mission["satellite"]["geometry"])
    satellite_record.subsystems = json.dumps(p_mission["satellite"]["subsystems"])
    satellite_record.instruments = json.dumps(p_mission["satellite"]["instruments"])
    satellite_record.save()
    mission_record.norad_id = p_mission["environment"]["norad_id"]
    mission_record.start_date = EnvironmentSimulator.mission_timer_to_datetime(p_mission["environment"]["start_date"])
    mission_record.mission_timer = p_mission["environment"]["elapsed_timer"]
    mission_record.tle_line_1 = p_mission["environment"]["tle_data"]["line_1"]
    mission_record.tle_line_2 = p_mission["environment"]["tle_data"]["line_2"]
    mission_record.satellite_ref = satellite_record
    mission_record.mission_hash = hash_id
    mission_record.save()
    return {"status":"ok", "mission_instance":p_mission}

def load_mission(hash_id):
    mission = {}
    mission_record = MissionInstance.objects.get(mission_hash=hash_id)
    mission["environment"] = EnvironmentSimulator.create_mission_environment(mission_record.norad_id, mission_record.start_date)
    mission["satellite"] = SatelliteSimulator.load_mission_satellite(mission_record.satellite_ref)
    return mission

def get_mission_logs(hash_id):
    # load all messages for a given mission
    json_data = {"status":"ok", "event_logs":[]}
    db_records = MissionEventLog.objects.get(mission_hash=hash_id)
    for item in db_records:
        json_data["event_logs"].append([item.timestamp, item.message])
    return json_data

def estimate_progress(p_mission):
    # check state of the mission vs expected result
    # has to be exposed via api call
    # check on mission objectives:
    #   photo taken - 25%
    #   photo with correct bounding box - 25%
    #   photo downloaded - 50%
    #   if 100% then mission completed, else continue
    pass


# Initialiaze on start
EnvironmentSimulator = CMSE_Env()
SatelliteSimulator = CMSE_Sat()
