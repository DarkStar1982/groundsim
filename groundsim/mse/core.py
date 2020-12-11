import json
from datetime import datetime, timezone, timedelta
from groundsim.mse.utils import parse_tle_lines, mission_timer_to_str, mission_timer_to_datetime
from groundsim.mse.aux_astro import get_orbital_data, time_since_periapsis
from groundsim.mse.sys_payload import get_imager_frame
################################################################################
########################## ENVIRONMENT SIMULATION CODE #########################
################################################################################

class CMSE_Env():
    def create_mission_environment(self, p_norad_id, p_start_date, tle_data):
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
        environment["tle_data"] = tle_data
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
        environment["event_logs"] = []
        return environment

    def increment_mission_timer(self, p_mission_timer, p_seconds):
        current_date = mission_timer_to_datetime(p_mission_timer)
        delta = timedelta(seconds=p_seconds)
        new_date = current_date + delta
        p_mission_timer["year"] = new_date.year
        p_mission_timer["month"] = new_date.month
        p_mission_timer["day"] = new_date.day
        p_mission_timer["hour"] = new_date.hour
        p_mission_timer["min"] = new_date.minute
        p_mission_timer["sec"] = new_date.second
        return p_mission_timer

    def log_event(self, p_environment, p_event_string):
        # save event  if mission exists in DB - TBD
        timestamp = mission_timer_to_str(p_environment["current_date"])
        p_environment["log_buffer"].append([timestamp, p_event_string])
        p_environment["event_logs"].append([timestamp, p_event_string])
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
        orbital_data = get_orbital_data(p_environment["tle_data"], p_environment["current_date"])
        p_environment["orbit_vector"] = [float(x) for x in orbital_data["gcrs_vector"]]
        p_environment["ground_track"] = {
            "lat": orbital_data["lat"],
            "lng": orbital_data["lng"],
            "alt": orbital_data["alt"]
        }
        p_environment["elements"] = {
            "a": float(orbital_data["elements"].semi_major_axis.km),
            "e": float(orbital_data["elements"].eccentricity),
            "i": float(orbital_data["elements"].inclination.degrees),
            "ra":float(orbital_data["elements"].longitude_of_ascending_node.degrees),
            "w": float(orbital_data["elements"].argument_of_periapsis.degrees),
            "tp":time_since_periapsis(orbital_data["elements"]),
        }
        event_message = "Test mission event %s" % int(p_environment["elapsed_timer"]/p_seconds)
        p_environment = self.log_event(p_environment, event_message)
        return p_environment

################################################################################
########################## SATELLITE SIMULATION CODE ###########################
################################################################################

class CMSE_Sat():
    # load physical model from database
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
                "fov":1.6, # degrees
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
        position_object["time"] = mission_timer_to_str(p_mission["environment"]["current_date"])
        position_object["lat"] = p_mission["environment"]["ground_track"]["lat"]
        position_object["lng"] = p_mission["environment"]["ground_track"]["lng"]
        position_object["alt"] = p_mission["environment"]["ground_track"]["alt"]
        position_object["a"] = p_mission["environment"]["elements"]["a"]
        position_object["e"] = p_mission["environment"]["elements"]["e"]
        position_object["i"] = p_mission["environment"]["elements"]["i"]
        position_object["ra"] = p_mission["environment"]["elements"]["ra"]
        position_object["w"] = p_mission["environment"]["elements"]["w"]
        position_object["tp"] = p_mission["environment"]["elements"]["tp"]
        position_object["status"] = "ok"
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

    # at 1 second resolution - input is Environment, output is new satellite
    def evolve_satellite(self, p_mission, p_seconds):
        p_mission["satellite"]["location"] = self.get_satellite_position(p_mission)
        p_mission["satellite"]["formatted_telemetry"] = self.get_satellite_telemetry(p_mission)
        p_mission["satellite"]["instruments"]["imager"]["frame"] = get_imager_frame(
            p_mission["satellite"]["instruments"]["imager"]["fov"],
            p_mission["environment"]["ground_track"]["alt"],
            p_mission["environment"]["ground_track"]["lat"],
            p_mission["environment"]["ground_track"]["lng"],
        )
        return p_mission["satellite"]

class CMSE_SceEng():
    # load db data
    def create_mission_scenario(self,p_scenario_id):
        scenario_data = {
            "scenario_id":p_scenario_id
        }
        return scenario_data

    # check state of the mission vs expected result
    # has to be exposed via api call
    # check on mission objectives example:
    #   photo taken - 25%
    #   photo with correct bounding box - 25%
    #   photo downloaded - 50%
    #   if 100% then mission completed, else continue
    def evaluate_progress(self, p_mission):
        return p_mission["scenario"]

    def execute_mission_action(self, p_mission, p_action):
        if action == "take_photo":
            pass
            # get imager frame
        return p_mission
