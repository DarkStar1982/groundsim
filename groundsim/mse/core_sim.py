import json
from datetime import datetime, timezone, timedelta
from groundsim.mse.core_utils import (
    parse_tle_lines,
    mission_timer_to_str,
    mission_timer_to_datetime,
    datetime_to_mission_timer,
    fp_equals
)
from groundsim.mse.lib_astro import get_orbital_data, time_since_periapsis
from groundsim.mse.sys_adcs import initialize_adcs_subsystem, simulate_adcs_subsystem
from groundsim.mse.sys_obdh import initialize_obdh_subsystem, simulate_obdh_subsystem
from groundsim.mse.sys_payload import get_imager_frame, take_imager_snapshot, initialize_payload_instruments
################################################################################
########################## ENVIRONMENT SIMULATION CODE #########################
################################################################################

class CMSE_Env():
    def create_mission_environment(self, p_norad_id, p_start_date, tle_data):
        environment = {}
        environment["norad_id"] = p_norad_id
        environment["current_date"] = p_start_date
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
        p_mission_timer = datetime_to_mission_timer(new_date)
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
    def create_mission_satellite(self, satellite_config):
        satellite = {
            "geometry":self.initialize_satellite_geometry(),
            "subsystems":self.initialize_satellite_subsystems(),
            "instruments":initialize_payload_instruments(satellite_config["config_instruments"]),
            "telemetry":self.initialize_satellite_telemetry(),
        }
        return satellite

    # should be loadable from DB data
    def initialize_satellite_subsystems(self):
        sat_components = {
            "power": {
                "solar_panels": {},
                "battery":{},
                "pdu":{},
                "power_bus":{}
            },
            "adcs": initialize_adcs_subsystem(None),
            "obdh": initialize_obdh_subsystem(None),
            "comm":{
                "receiver":{},
                "transmitter":{},
            },
            "dbus":{}
        }
        return sat_components

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

    # refactor ME - TBD
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

    # simulate each subsystem at 1 sec resolution
    def evolve_satellite(self, p_mission, p_seconds):
        p_mission["satellite"]["location"] = self.get_satellite_position(p_mission)
        p_mission["satellite"]["formatted_telemetry"] = self.get_satellite_telemetry(p_mission)

        # simulatate subsystems
        p_mission["satellite"]["subsystems"]["adcs"], p_mission["satellite"]["subsystems"]["dbus"] =  simulate_adcs_subsystem(p_mission["satellite"]["subsystems"]["adcs"], p_mission["satellite"]["subsystems"]["dbus"], p_seconds)
        p_mission["satellite"]["subsystems"]["obdh"], p_mission["satellite"]["subsystems"]["dbus"] = simulate_obdh_subsystem(p_mission["satellite"]["subsystems"]["obdh"], p_mission["satellite"]["subsystems"]["dbus"], p_seconds)

        # simulate instrument operation
        p_mission["satellite"]["instruments"]["imager"]["frame"] = get_imager_frame(
            p_mission["satellite"]["instruments"]["imager"]["fov"],
            p_mission["environment"]["ground_track"]["alt"],
            p_mission["environment"]["ground_track"]["lat"],
            p_mission["environment"]["ground_track"]["lng"],
        )
        return p_mission["satellite"]

################################################################################
########################### MISSION SCENARIO ENGINE ############################
################################################################################
class CMSE_SceEng():
    def initialize_scenario(self, p_mission, p_scenario_data):
        p_mission["scenario"] = p_scenario_data
        p_mission["scenario"]["progress"] = 0
        points_to_win = 0
        for item in p_mission["scenario"]["objectives"]:
            points_to_win += item["score_points"]
        # once acculumated points reach or exceed this value, the scenario is considered completed
        p_mission["scenario"]["points_to_win"] = points_to_win
        return p_mission["scenario"]

    def is_objective_completed(self, p_mission, p_objective):
        fp_precision = p_mission["scenario"]["initial_setup"]["fp_precision"]
        result = False
        if p_objective["type"] == "take_photo":
            for item in p_mission["satellite"]["instruments"]["imager"]["buffer"]:
                result = fp_equals(item["image_box"]["top"], p_objective["definition"]["top"], fp_precision)
                result = result and fp_equals(item["image_box"]["left"], p_objective["definition"]["left"], fp_precision)
                result = result and fp_equals(item["image_box"]["bottom"], p_objective["definition"]["bottom"], fp_precision)
                result = result and fp_equals(item["image_box"]["right"], p_objective["definition"]["right"], fp_precision)
                if result:
                    return result
        return result

    def evaluate_progress(self, p_mission):
        for item in p_mission["scenario"]["objectives"]:
            if self.is_objective_completed(p_mission, item):
                p_mission["scenario"]["progress"] += item["score_points"]
        return p_mission["scenario"]

    def execute_mission_action(self, p_mission, p_action):
        if p_action == "take_photo":
            p_mission = take_imager_snapshot(p_mission)
        return p_mission
