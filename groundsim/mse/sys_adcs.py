def initialize_adcs_subsystem(p_adcs_definition):
    p_adcs_subsystem = {
        "ADCS_MODE": "UNDEFINED",
        "IMU":{},
        "GPS":{
            "LAT":0.0,
            "LON":0.0,
            "ALT":0.0
        }
    }
    return p_adcs_subsystem

# TBD - hardware support for GPS data
def set_location(p_adcs_subsystem, p_location):
    # set location
    p_adcs_subsystem["GPS"]["LAT"]= p_location["lat"]
    p_adcs_subsystem["GPS"]["LON"]= p_location["lng"]
    p_adcs_subsystem["GPS"]["ALT"]= p_location["alt"]
    return p_adcs_subsystem

def write_to_data_bus(data_bus, p_adcs_subsystem):
    data_bus["adcs"]["out"]["gps_lat"] = p_adcs_subsystem["GPS"]["LAT"]
    data_bus["adcs"]["out"]["gps_lng"] = p_adcs_subsystem["GPS"]["LON"]
    data_bus["adcs"]["out"]["gps_alt"] = p_adcs_subsystem["GPS"]["ALT"]
    return data_bus

def simulate_adcs_subsystem(p_adcs_subsystem, p_mission, p_seconds):
    data_bus = p_mission["satellite"]["subsystems"]["dbus"]
    location = p_mission["satellite"]["location"]
    p_adcs_subsystem = set_location(p_adcs_subsystem, location)
    data_bus = write_to_data_bus(data_bus, p_adcs_subsystem)
    return p_adcs_subsystem, data_bus
