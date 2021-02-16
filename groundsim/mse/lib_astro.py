from math import pi, cos, exp, pow, sin, sqrt, radians
from skyfield.api import EarthSatellite, load
from skyfield.elementslib import osculating_elements_of

################################################################################
################################# GLOBAL VALUES ################################
################################################################################
UTC_DAY = 86400
SIDEREAL_DAY = 86164.0905
R_EARTH = 6378137.0
E_2 = 6.69437999014E-3

# ephemeris are loaded on instantiation
JPL_EPH = load('de421.bsp')

################################################################################
# calculate orbital vector and ground track from the following:
#   -> TLE element set
#   -> time (in UTC)
# return
#   <- ground track position
#   <- orbital vector
#   <- osculating orbital elements
#   <- day/night flag
################################################################################
def get_orbital_data(tle_data, time_data, label="Satellite"):
    ts = load.timescale()
    satellite = EarthSatellite(tle_data["line_1"], tle_data["line_2"], label, ts)
    time_instant = ts.utc(
        time_data["year"],
        time_data["month"],
        time_data["day"],
        time_data["hour"],
        time_data["min"],
        time_data["sec"],
    )
    geocentric = satellite.at(time_instant)
    subpoint = geocentric.subpoint()
    elements = osculating_elements_of(geocentric)
    result = {
        "description":str(satellite),
        "lat":float(subpoint.latitude.degrees),
        "lng":float(subpoint.longitude.degrees),
        "alt":float(subpoint.elevation.km),
        "sunlit": satellite.at(time_instant).is_sunlit(JPL_EPH),
        "gcrs_vector":geocentric.position.km,
        "elements": elements
    }
    return result

def get_adcs_vectors(time_data):
    sun = JPL_EPH['sun']
    earth = JPL_EPH['earth']
    ts = load.timescale()
    time_instant = ts.utc(
        time_data["year"],
        time_data["month"],
        time_data["day"],
        time_data["hour"],
        time_data["min"],
        time_data["sec"],
    )

    sun_vector = sun.at(time_instant).position.au
    earth_vector = earth.at(time_instant).position.au

    norm_e = 0.0
    norm_s = 0.0
    for item in earth_vector:
        norm_e = norm_e + pow(item,2)
    norm_e = sqrt(norm_e)
    for item in sun_vector:
        norm_s = norm_s + pow(item,2)
    norm_s = sqrt(norm_s)
    return { "e_v":[x/norm_e for x in earth_vector], "s_v":[y/norm_s for y in sun_vector] }

################################################################################
# output is in seconds
################################################################################
def time_since_periapsis(p_orbital_elements):
    t_since_periapsis = float(UTC_DAY*p_orbital_elements.period_in_days * p_orbital_elements.true_anomaly.degrees/360)
    return t_since_periapsis

################################################################################
# calculates length of one degree longitude/latidude across the globe
# input should be in degrees, output is in km
################################################################################
def calculate_degree_length(p_lat):
    # calculate latitude degree length
    lat = radians(p_lat)
    length_lat = 111132.954 - 559.822 * cos(2*lat)+1.175 * cos(4*lat)
    length_lon = (pi * R_EARTH * cos (lat))/(180*sqrt(1-E_2*pow(sin(lat),2)))
    return {"length_lon":length_lon/1000.0, "length_lat":length_lat/1000.0}
