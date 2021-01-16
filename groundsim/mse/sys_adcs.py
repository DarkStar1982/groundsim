ADCS_MODES = {
    "UNSET": 1,
    "TRACK": 2,
    "BDOTT": 3,
    "TOSUN": 4,
    "NADIR": 5
}

def initialize_adcs_subsystem(p_adcs_definition):
    p_adcs_subsystem = {
        "ADCS_MODE": ADCS_MODES["UNSET"],
        "IMU":{}, #<- quaternions
        "GPS":{
            "LAT":0.0,
            "LON":0.0,
            "ALT":0.0,
            "TME":0
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
    data_bus["gps"]["out"]["lat"] = p_adcs_subsystem["GPS"]["LAT"]
    data_bus["gps"]["out"]["lng"] = p_adcs_subsystem["GPS"]["LON"]
    data_bus["gps"]["out"]["alt"] = p_adcs_subsystem["GPS"]["ALT"]
    data_bus["gps"]["out"]["tme"] = p_adcs_subsystem["GPS"]["TME"]
    data_bus["adc"]["out"]["mode"] = p_adcs_subsystem["ADCS_MODE"]
    return data_bus

def simulate_adcs_subsystem(p_adcs_subsystem, p_mission, p_seconds):
    data_bus = p_mission["satellite"]["subsystems"]["dbus"]
    location = p_mission["satellite"]["location"]
    p_adcs_subsystem = set_location(p_adcs_subsystem, location)
    data_bus = write_to_data_bus(data_bus, p_adcs_subsystem)
    return p_adcs_subsystem, data_bus
