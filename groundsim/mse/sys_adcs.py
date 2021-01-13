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

def simulate_adcs_subsystem(p_adcs_subsystem, p_dbus, p_seconds):
    return p_adcs_subsystem, p_dbus
