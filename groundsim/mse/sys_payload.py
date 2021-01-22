from math import pi, tan, radians, atan, degrees
from groundsim.mse.lib_astro import calculate_degree_length

# camera FOV calculation
# d - sensor diagonal
# f - effective focal length
def calculate_camera_fov(d,f):
    alpha = 2*atan(d/(2*f))
    return degrees(alpha)

# camera GSD calculation
# p_alt - altitude, in km
# p_size - pixel size
# p_f - focal length
def calculate_camera_gsd(p_alt, p_size, p_f):
    return 1000*p_alt*p_size/p_f

# camera 1D swath length
# input in degrees and km, output in km
def calculate_swath(p_ifov, p_alt):
    ifov = radians(p_ifov)
    d = 2*p_alt*tan(ifov/2)
    return d

def get_imager_frame(p_ifov, p_alt, p_lat, p_lon):
    swath = calculate_swath(p_ifov, p_alt)
    deg_length = calculate_degree_length(p_lat)
    swath_lat = swath/deg_length["length_lat"]
    swath_lon = swath/deg_length["length_lon"]
    result = {
        "top": max(p_lat + swath_lat/2, p_lat - swath_lat/2),
        "left": min(p_lon + swath_lon/2, p_lon - swath_lon/2),
        "bottom": min(p_lat + swath_lat/2,p_lat - swath_lat/2),
        "right":max(p_lon + swath_lon/2,p_lon - swath_lon/2)
    }
    return result

def take_imager_snapshot(p_mission):
    snapshot = {
        "image_box":p_mission["satellite"]["instruments"]["imager"]["frame"],
        "timestamp":p_mission["environment"]["current_date"]
    }
    p_mission["satellite"]["instruments"]["imager"]["buffer"].append(snapshot)
    p_mission["satellite"]["instruments"]["imager"]["counter"]+=1
    return p_mission

# should be loaded from external source
def initialize_payload_instruments(instrument_data):
    instruments = {
        "imager": {
            "fov":instrument_data["imager"]["fov"],
            "d":instrument_data["imager"]["d"],
            "f":instrument_data["imager"]["f"],
            "sensor":instrument_data["imager"]["sensor"],
            "pixel":instrument_data["imager"]["pixel"],
            "counter":0,
            "buffer":[],
            "gain_r":1.0,
            "gain_g":1.0,
            "gain_b":1.0,
            "expose":1.0,
        },
        # sdr:{}, TBD
    }
    return instruments
