from skyfield.api import EarthSatellite, load
from skyfield.elementslib import osculating_elements_of

# ephemeris loading
JPL_EPH = load('de421.bsp')

################################################################
# calculate orbital vector and ground track from the following
# -> TLE set
# -> time (in UTC)
# return
# <- ground track position
# <- osculating orbital elements
# <- day/night flag
################################################################
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
