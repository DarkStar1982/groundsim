import json
from hashlib import sha256
from groundsim.models import (
    Satellite,
    SatelliteInstance,
    MissionInstance,
    MissionEventLog,
    MissionScenario,
    UserInstance
)
from groundsim.mse.core_sim import CMSE_Env, CMSE_Sat, CMSE_SceEng
from groundsim.mse.lib_utils import datetime_to_mission_timer, mission_timer_to_datetime

################################################################################
############################# DATABASE I/O ACTIONS #############################
################################################################################
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
            {
            "sat_name":item.satellite_name,
            "norad_id":item.norad_id
            }
        )
    resp_sats["status"] = "ok"
    resp_sats["satelites"] = sat_list
    return resp_sats

def get_tle_data(norad_id):
    satellite_record = Satellite.objects.get(norad_id=norad_id)
    return {
        "line_1":satellite_record.satellite_tle1,
        "line_2":satellite_record.satellite_tle2
    }

def get_scenario_data(p_scenario_id):
    try:
        scenario_obj = MissionScenario.objects.get(scenario_id=p_scenario_id)
        scenario_data = {
            "scenario_id":scenario_obj.scenario_id,
            "objectives":[],
            "progress":0,
            "fp_precision":0.001,
            "start_date":{
                "year":scenario_obj.start_date.year,
                "month":scenario_obj.start_date.month,
                "day":scenario_obj.start_date.day,
                "hour":scenario_obj.start_date.hour,
                "min":scenario_obj.start_date.minute,
                "sec": scenario_obj.start_date.second
            },
            "mission_name": scenario_obj.mission_name,
            "description": scenario_obj.description,
            "initial_setup": json.loads(scenario_obj.initial_setup),
            "objectives": json.loads(scenario_obj.objectives)
        }
    except MissionScenario.DoesNotExist:
        scenario_data =  {
            "scenario_id":0,
            "objectives":[],
        }
    return scenario_data

def get_satellite_config(p_norad_id):
    try:
        satellite_record = Satellite.objects.get(norad_id=p_norad_id)
        satellite_obj = {
            "config_instruments":json.loads(satellite_record.config_instrument)
        }
    except Satellite.DoesNotExist:
        satellite_obj = None
    return satellite_obj

def get_mission_logs(hash_id):
    # load all messages for a given mission
    json_data = {"status":"ok", "event_logs":[]}
    db_records = MissionEventLog.objects.get(mission_hash=hash_id)
    for item in db_records:
        json_data["event_logs"].append([item.timestamp, item.message])
    return json_data

def write_mission_logs(p_environment):
    if p_environment["hash_id"] is not None:
        hash_id = p_environment["hash_id"]
        mission_record = MissionInstance.objects.get(mission_hash=hash_id)
        event_record = MissionEventLog()
        event_record.mission_ref = mission_record
        event_record.timestamp = mission_timer_to_datetime(p_environment["current_date"])
        event_record.message = p_event_string
        event_record.save()
    if len(p_environment["event_logs"])>10:
        p_environment["event_logs"].pop(0)
    return p_environment

def write_user(p_user, p_email):
    record, created = UserInstance.objects.get_or_create(user=p_user, email = p_email)
    return record

################################################################################
######################## TIER 1 API - BASIC ACTIONS API ########################
################################################################################
def get_instrument_list():
    instruments = []

    # read from DB properly instead
    satellite_records = Satellite.objects.all()
    for record in satellite_records:
        instrument_obj ={
            "instrument":json.loads(record.config_instrument),
            "id":record.norad_id
        }
        instruments.append(instrument_obj)
    return instruments

def get_target_passes():
    return []

################################################################################
###################### TIER 2 API - MISSION SIMULATION API #####################
################################################################################
def create_mission_instance(p_norad_id, p_scenario_id, p_start_date):
    mission = {}
    if p_scenario_id == 0:
        norad_id = p_norad_id
        start_date = datetime_to_mission_timer(p_start_date)
        tle_data = get_tle_data(norad_id)
        scenario_data = { "scenario_id":0, "objectives":[] }
    else:
        scenario_data = get_scenario_data(p_scenario_id)
        norad_id = scenario_data["initial_setup"]["norad_id"]
        start_date = scenario_data["start_date"]
        tle_data = get_tle_data(norad_id)
    satellite_config = get_satellite_config(norad_id)
    mission["environment"] = EnvironmentSimulator.create_mission_environment(norad_id, start_date, tle_data)
    mission["satellite"] = SatelliteSimulator.create_mission_satellite(satellite_config)
    mission["scenario"] = ScenarioEngine.initialize_scenario(mission, scenario_data)
    return mission

def simulate_mission_steps(p_mission, steps):
    p_mission["environment"] = EnvironmentSimulator.evolve_environment(p_mission["environment"], steps)
    p_mission["satellite"] = SatelliteSimulator.evolve_satellite(p_mission, steps)
    p_mission["scenario"] = ScenarioEngine.evaluate_progress(p_mission)
    p_mission["environment"] = write_mission_logs(p_mission["environment"])
    return p_mission


# check if mission record already exists before saving
def save_mission(p_mission, p_user, p_email):
    if p_mission["environment"]["user"] is None and p_mission["environment"]["email"] is None:
        hash_id = sha256(json.dumps(p_mission).encode('utf-8')).hexdigest()
        user_record = write_user(p_user, p_email)
        user_record.save()
        mission_record = MissionInstance()
        satellite_record = SatelliteInstance()
        p_mission["environment"]["user"] = p_user
        p_mission["environment"]["email"] = p_email
        p_mission["environment"]["hash_id"] = hash_id
        mission_record.mission_hash = hash_id
        mission_record.user_ref = user_record
        mission_record.save()
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
    mission_record.start_date = mission_timer_to_datetime(p_mission["environment"]["start_date"])
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
    tle_data = get_tle_data(mission_record.norad_id)
    scenario_data = get_scenario_data(mission_record.scenario_ref.scenario_id)
    mission["environment"] = EnvironmentSimulator.create_mission_environment(mission_record.norad_id, mission_record.start_date, tle_data)
    mission["satellite"] = SatelliteSimulator.load_mission_satellite(mission_record.satellite_ref)
    mission["scenario"] = ScenarioEngine.initialize_scenario(mission, scenario_data)
    return mission

def execute_mission_action(p_mission, p_action):
    p_mission = ScenarioEngine.execute_mission_action(p_mission, p_action)
    return p_mission

# Initialiaze on start
EnvironmentSimulator = CMSE_Env()
SatelliteSimulator = CMSE_Sat()
ScenarioEngine = CMSE_SceEng()
