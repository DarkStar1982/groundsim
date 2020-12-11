import json
from hashlib import sha256
from groundsim.models import Satellite, SatelliteInstance, MissionInstance, UserInstance, MissionEventLog
from groundsim.mse.core import CMSE_Env, CMSE_Sat, CMSE_SceEng
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

def get_tle_data(norad_id):
    satellite_record = Satellite.objects.get(norad_id=norad_id)
    return {
        "line_1":satellite_record.satellite_tle1,
        "line_2":satellite_record.satellite_tle2
    }

def create_mission_instance(norad_id, scenario_id, start_date):
    mission = {}
    tle_data = get_tle_data(norad_id)
    mission["environment"] = EnvironmentSimulator.create_mission_environment(norad_id, start_date, tle_data)
    mission["satellite"] = SatelliteSimulator.create_mission_satellite()
    mission["scenario"] = ScenarioEngine.create_mission_scenario(scenario_id)
    return mission

def write_logs(p_environment):
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

def simulate_mission_steps(p_mission, steps):
    p_mission["environment"] = EnvironmentSimulator.evolve_environment(p_mission["environment"], steps)
    p_mission["satellite"] = SatelliteSimulator.evolve_satellite(p_mission, steps)
    p_mission["scenario"] = ScenarioEngine.evaluate_progress(p_mission)
    # save mission log - TBD
    p_mission["environment"] = write_logs(p_mission["environment"])
    return p_mission

def save_user(p_user, p_email):
    record, created = UserInstance.objects.get_or_create(user=p_user, email = p_email)
    return record

# check if mission record already exists before saving
def save_mission(p_mission, p_user, p_email):
    if p_mission["environment"]["user"] is None and p_mission["environment"]["email"] is None:
        hash_id = sha256(json.dumps(p_mission).encode('utf-8')).hexdigest()
        user_record = save_user(p_user, p_email)
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
    tle_data = get_tle_data(mission_record.norad_id)
    mission["environment"] = EnvironmentSimulator.create_mission_environment(mission_record.norad_id, mission_record.start_date, tle_data)
    mission["satellite"] = SatelliteSimulator.load_mission_satellite(mission_record.satellite_ref)
    mission["scenario"] = ScenarioEngine.create_mission_scenario(mission_record.scenario_ref.scenario_id)
    return mission

def get_mission_logs(hash_id):
    # load all messages for a given mission
    json_data = {"status":"ok", "event_logs":[]}
    db_records = MissionEventLog.objects.get(mission_hash=hash_id)
    for item in db_records:
        json_data["event_logs"].append([item.timestamp, item.message])
    return json_data

def execute_mission_action(p_mission, p_action):
    p_mission = ScenarioEngine.execute_mission_action(p_mission)
    return p_mission

# Initialiaze on start
EnvironmentSimulator = CMSE_Env()
SatelliteSimulator = CMSE_Sat()
ScenarioEngine = CMSE_SceEng()
