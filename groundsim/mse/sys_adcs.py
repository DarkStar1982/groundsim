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
        "SYS_CLOCK":0.0,
        "MODE_TIME":0.0,
        "IMU":{
            "SUN_X":0.0,
            "SUN_Y":0.0,
            "SUN_Z":0.0,
            "MAG_X":0.0,
            "MAG_Y":0.0,
            "MAG_Z":0.0,
            "ANG_X":0.0,
            "ANG_Y":0.0,
            "ANG_Z":0.0,
            "QAT_A":0.0,
            "QAT_B":0.0,
            "QAT_C":0.0,
            "QAT_D":0.0
        },
        "MTQ":{
            "MTQ_X":0.0,
            "MTQ_Y":0.0,
            "MTQ_Z":0.0
        },
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

def sync_time(p_adcs_subsystem, p_time):
    p_adcs_subsystem["SYS_CLOCK"] = p_time
    return p_adcs_subsystem

def write_to_data_bus(data_bus, p_adcs_subsystem):
    data_bus["adc"]["out"]["mode"] = p_adcs_subsystem["ADCS_MODE"]
    data_bus["adc"]["out"]["gps"]["lat"] = p_adcs_subsystem["GPS"]["LAT"]
    data_bus["adc"]["out"]["gps"]["lng"] = p_adcs_subsystem["GPS"]["LON"]
    data_bus["adc"]["out"]["gps"]["alt"] = p_adcs_subsystem["GPS"]["ALT"]
    data_bus["adc"]["out"]["gps"]["tme"] = p_adcs_subsystem["GPS"]["TME"]

    data_bus["adc"]["out"]["imu"]["sun_x"] = p_adcs_subsystem["IMU"]["SUN_X"]
    data_bus["adc"]["out"]["imu"]["sun_y"] = p_adcs_subsystem["IMU"]["SUN_Y"]
    data_bus["adc"]["out"]["imu"]["sun_z"] = p_adcs_subsystem["IMU"]["SUN_Z"]

    data_bus["adc"]["out"]["imu"]["ang_x"] = p_adcs_subsystem["IMU"]["ANG_X"]
    data_bus["adc"]["out"]["imu"]["ang_y"] = p_adcs_subsystem["IMU"]["ANG_Y"]
    data_bus["adc"]["out"]["imu"]["ang_z"] = p_adcs_subsystem["IMU"]["ANG_Z"]

    data_bus["adc"]["out"]["imu"]["mag_x"] = p_adcs_subsystem["IMU"]["MAG_X"]
    data_bus["adc"]["out"]["imu"]["mag_y"] = p_adcs_subsystem["IMU"]["MAG_Y"]
    data_bus["adc"]["out"]["imu"]["mag_z"] = p_adcs_subsystem["IMU"]["MAG_Z"]

    data_bus["adc"]["out"]["imu"]["qat_a"] = p_adcs_subsystem["IMU"]["QAT_A"]
    data_bus["adc"]["out"]["imu"]["qat_b"] = p_adcs_subsystem["IMU"]["QAT_B"]
    data_bus["adc"]["out"]["imu"]["qat_c"] = p_adcs_subsystem["IMU"]["QAT_C"]
    data_bus["adc"]["out"]["imu"]["qat_d"] = p_adcs_subsystem["IMU"]["QAT_D"]

    data_bus["adc"]["out"]["mtq"]["mtq_x"] = p_adcs_subsystem["MTQ"]["MTQ_X"]
    data_bus["adc"]["out"]["mtq"]["mtq_y"] = p_adcs_subsystem["MTQ"]["MTQ_Y"]
    data_bus["adc"]["out"]["mtq"]["mtq_z"] = p_adcs_subsystem["MTQ"]["MTQ_Z"]
    return data_bus

def process_command_queue(p_adcs_subsystem, p_com_queue):
    if len(p_com_queue)>0:
        for item in p_com_queue:
            command = item[0]
            attributes = item[1]
            if command == "SET_MODE":
                p_adcs_subsystem["ADCS_MODE"] = attributes[0]
                p_adcs_subsystem["MODE_TIME"] = attributes[1]
    return p_adcs_subsystem

def simulate_process(p_adcs_subsystem):
    return p_adcs_subsystem

def simulate_adcs_subsystem(p_adcs_subsystem, p_mission, p_seconds):
    data_bus = p_mission["satellite"]["subsystems"]["dbus"]
    location = p_mission["satellite"]["location"]
    time = p_mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VCPU"]["VXM_CLOCK"]/1000
    p_adcs_subsystem = set_location(p_adcs_subsystem, location)
    p_adcs_subsystem = sync_time(p_adcs_subsystem, time)
    p_adcs_subsystem = process_command_queue(p_adcs_subsystem, data_bus["adc"]["inq"])
    p_adcs_subsystem = simulate_process(p_adcs_subsystem)
    data_bus = write_to_data_bus(data_bus, p_adcs_subsystem)
    return p_adcs_subsystem, data_bus
