# mission simulation environment:
# environment simulator + satellite system simulator
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv

# Global Constants


class EnvironmentSimulation():
    # start date, NORAD ID, mode, ground station locations?
    def __init__(self, p_norad_id, p_start_date):
        self.norad_id = p_norad_id
        self.start_date = p_start_date
        self.mission_timer = 0
        self.orbit_vector = None
        self.sun_vector = None
        self.ground_stations = []

        self.evolve_step_forward()

    # at 1 second resolution
    def evolve_step_forward():
        self.orbit_vector = self.compute_orbit()
        self.mission_timer = self.mission_timer + 1
        #... and so on

    def reset_to_start():
        pass

    def get_state():
        return {
            "timer": self.mission_timer
        }

class SatelliteSimulation():
    # satellite configuration:
    def __init__(self):
        pass

    # at 1 second resolution - input is Environment simulation output
    def evolve_step_forward():
        pass

    # should include ground station visibility calculation
    def queue_command():
        pass

    def get_state():
        pass

    # ???
    def get_event_log():
        pass
