import julian
import calendar
from datetime import datetime
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
from math import fmod, pi, tan, atan, sqrt, sin, fabs, cos, atan2, trunc, acos

################################################################################
############################### GLOBAL CONSTANTS ###############################
################################################################################

J2 = 1.08E-3 # second harmonic
MU_EARTH = 3.986E14

################################################################################
############################# HELPER FUNCTIONS CODE ############################
################################################################################
def mission_timer_to_str(p_mission_timer):
    str_timer = "%02i:%02i:%02i, %02i %s %s" % (
        p_mission_timer["hour"],
        p_mission_timer["min"],
        p_mission_timer["sec"],
        p_mission_timer["day"],
        calendar.month_abbr[p_mission_timer["month"]],
        p_mission_timer["year"],
    )
    return str_timer

def mission_timer_to_datetime(p_mission_timer):
    packed_date = datetime(
        p_mission_timer["year"],
        p_mission_timer["month"],
        p_mission_timer["day"],
        p_mission_timer["hour"],
        p_mission_timer["min"],
        p_mission_timer["sec"]
    )
    return packed_date

def get_epoch_time(tle_string):
    year = int(tle_string[0:2])
    if year<57:
        year = 2000 + year
    else:
        year = 1957 + year
    days =  float(tle_string[2:])
    date_a = datetime(year, 1, 1,tzinfo=timezone.utc) + timedelta(days - 1)
    return date_a

def convert_to_float(element):
    if element[0] == '-':
        sign = '-'
        mantissa = element[1:5]
        exponent = element[-1]
    else:
        sign = ''
        mantissa = element[0:4]
        exponent = element[-1]
    value = sign + '0.'+ mantissa +'E-' + exponent
    return float(value)

# floating point comparison
def fp_equals(a,b,c):
    if fabs(fabs(a)-fabs(c))<c:
        return True
    else:
        return False

# camera calculations
def calculate_camera_fov(d,f):
    alpha = 2*atan(d/(2*f))
    return alpha

def parse_tle_lines(tle_line_1, tle_line_2):
    tle_data = {}
    line_1 = [x for x in tle_line_1.split(' ') if len(x)>0]
    # insert whitespace to correctly process last two elements - maybe optional!
    if tle_line_2[-5] !=' ':
        line3 = tle_line_2[0:-4] + ' '+ tle_line_2[-4:]
    line_2 = [x for x in line3.split(' ') if len(x)>0]
    tle_data["catalog_number"] = int(line_1[1][:-1])
    tle_data["classification"] = line_1[1][-1]
    tle_data["launch_label"] = line_1[2]
    tle_data["epoch_date"] = line_1[3]
    tle_data["first_derivative"] = float(line_1[4])
    tle_data["second_derivative"] = convert_to_float(line_1[5])
    tle_data["drag_term"] = convert_to_float(line_1[6])
    tle_data["ephemeris_type"] = int(line_1[7])
    tle_data["element_set_type"] = int(line_1[8])
    tle_data["inclination"] = float(line_2[2])
    tle_data["ra_ascending_node"] = float(line_2[3])
    tle_data["eccentricity"] = float('0.'+line_2[4])
    tle_data["argument_perigee"] = float(line_2[5])
    tle_data["mean_anomaly"] = float(line_2[6])
    tle_data["mean_motion"] = float(line_2[7])
    tle_data["revolution_number"] = int(line_2[8][:-1])
    return tle_data

def convert_to_geodetic(tle_data, position, date):
    geo_data = {}
    # copy the data from SGP4 output
    x = position[0]
    y = position[1]
    z = position[2]
    # longitude calculation
    jd = julian.to_jd(date)
    ut = fmod(jd + 0.5, 1.0)
    t = (jd - ut - 2451545.0) / 36525.0
    omega = 1.0 + 8640184.812866 / 3155760000.0;
    gmst0 = 24110.54841 + t * (8640184.812866 + t * (0.093104 - t * 6.2E-6))
    theta_GMST = fmod(gmst0 + 86400* omega * ut, 86400) * 2 * pi / 86400
    lon = atan2(y,x)-theta_GMST
    lon = lon*180/pi
    geo_data["lng"] = lon
    if lon<-180:
        geo_data["lng"] = 360 + lon
    if lon>-180:
        geo_data["lng"] = lon
    # latitude calculation
    lat = atan(z/sqrt(x*x + y*y))
    a = 6378.137
    e = 0.081819190842622
    delta = 1.0
    while (delta>0.001):
        lat0 = lat
        c = (a * e * e * sin(lat0))/sqrt(1.0 - e * e * sin(lat0) * sin(lat0))
        lat = atan((z + c)/sqrt(x*x + y*y))
        delta = fabs(lat - lat0)
    geo_data["lat"] = 180*lat/pi
    #altitude calculation
    if f_equals(lat,pi/2,0.01):
        alt = z/sin(lat) - a*sqrt(1-e*e)
    else:
        alt = sqrt(x*x + y*y)/cos(lat) - a/sqrt(1.0 - e*e*sin(lat)*sin(lat))
    geo_data["alt"] = fabs(alt)
    return geo_data

def propagate_orbit(tle_data, mission_timer):
    satellite_object = twoline2rv(tle_data["line_1"], tle_data["line_2"], wgs72)
    position, velocity = satellite_object.propagate(
        mission_timer["year"],
        mission_timer["month"],
        mission_timer["day"],
        mission_timer["hour"],
        mission_timer["min"],
        mission_timer["sec"]
    )
    return {"orbit_position": position, "orbit_velocity":velocity}

def get_ground_track(self, tle_data, orbital_vector, p_date):
    current_date = datetime(
        p_date["year"],
        p_date["month"],
        p_date["day"],
        p_date["hour"],
        p_date["min"],
        p_date["sec"]
    )
    tle_object = parse_tle_lines(tle_data["line_1"], tle_data["line_2"])
    ground_track = convert_to_geodetic(
        tle_object,
        orbital_vector["orbit_position"],
        current_date
    )
    return ground_track
