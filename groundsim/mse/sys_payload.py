from math import pi, tan, radians
from groundsim.mse.aux_astro import calculate_degree_length

# camera FOV calculation
def calculate_camera_fov(d,f):
    alpha = 2*atan(d/(2*f))
    return alpha

# camera 1D swath length
# input in degrees, output in km
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


def initialize_payload_instruments():
    instruments = {
        "imager": {
            "fov":1.6, # in degrees
            "f":0.58,
            "sensor":[4096,3072],
            "pixel":5.5E-6,
            "counter":0,
            "buffer":[]
        },
        "sdr": {}
    }
    return instruments