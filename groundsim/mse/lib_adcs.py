from skyfield.api import EarthSatellite, load
JPL_EPH = load('de421.bsp')

def get_adcs_vectors(time_data, tle_data):
    sun = JPL_EPH['sun']
    earth = JPL_EPH['earth']
    ts = load.timescale()
    label="Satellite"
    satellite = EarthSatellite(tle_data["line_1"], tle_data["line_2"], label, ts)
    time_instant = ts.utc(
        time_data["year"],
        time_data["month"],
        time_data["day"],
        time_data["hour"],
        time_data["min"],
        time_data["sec"],
    )
    tru_pos = earth + satellite
    sun_vector1 = tru_pos.at(time_instant).observe(sun).apparent().position.km
    sun_vector2 = satellite.at(time_instant).position.km
    # sun_vector = satellite.at(time_instant).observe(earth).apparent()
    # print(tru_pos.at(time_instant).position.km)
    # print(earth.at(time_instant).position.km)
    return [sun_vector1 - sun_vector2]
