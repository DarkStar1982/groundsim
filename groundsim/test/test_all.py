from django.test import TestCase
from math import radians, isclose
from skyfield.api import EarthSatellite, load
from groundsim.mse.lib_astro import get_orbital_data, time_since_periapsis, calculate_degree_length
from groundsim.mse.sys_payload import calculate_camera_gsd, calculate_camera_fov, calculate_swath, get_imager_frame
from groundsim.mse.core_sim import CMSE_Env, CMSE_Sat, CMSE_SceEng

class TestBaseClass(TestCase):
    def fp_eq(self, a, b):
        return isclose(a, b , abs_tol=self.fp_epsilon)

class AstroTestCases(TestBaseClass):
    def setUp(self):
        self.tle_data = {
            "line_1":'1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082',
            "line_2":'2 25544  51.6498 109.4756 0003572  55.9686 274.8005 15.49815350868473'
        }
        self.time_data = {
            "year":2014,
            "month":1,
            "day":23,
            "hour":11,
            "min":18,
            "sec": 7
        }
        self.fp_epsilon = 0.001

    def test_get_orbital_data(self):
        result = get_orbital_data(self.tle_data, self.time_data)
        assert(self.fp_eq(result["lat"], 50.243) == True)
        assert(self.fp_eq(result["lng"], -86.389) == True)
        assert(self.fp_eq(result["alt"], 420.874) == True)
        assert(self.fp_eq(result["gcrs_vector"][0], -3918.876) == True)
        assert(self.fp_eq(result["gcrs_vector"][1], -1887.648) == True)
        assert(self.fp_eq(result["gcrs_vector"][2], 5209.088) == True)
        assert(result["sunlit"] == False)
        assert(self.fp_eq(result["elements"].semi_major_axis.km, 6790.297) == True)
        assert(isclose(result["elements"].eccentricity, 0.0007679, abs_tol=0.000001) == True)
        assert(self.fp_eq(result["elements"].inclination.degrees,51.710) == True)
        assert(self.fp_eq(result["elements"].longitude_of_ascending_node.degrees, 96.701) == True)
        assert(self.fp_eq(result["elements"].argument_of_periapsis.degrees, 60.161) == True)
        assert(self.fp_eq(result["elements"].true_anomaly.degrees, 41.894) == True)

    def test_time_since_periapsis(self):
        data = get_orbital_data(self.tle_data, self.time_data)
        result = time_since_periapsis(data["elements"])
        assert(isclose(result,648.036,abs_tol=self.fp_epsilon)==True)

    def test_calculate_degree_length(self):
        test_data = [
            [0, 110.574, 111.320],
            [15, 110.649, 107.55],
            [30, 110.852, 96.486],
            [45, 111.132, 78.847],
            [60, 111.412, 55.800],
            [75, 111.618, 28.902],
            [90, 111.694, 0.0000]
        ]
        for item in test_data:
            result = calculate_degree_length(item[0])
            assert(self.fp_eq(result["length_lat"], item[1]) == True)
            assert(self.fp_eq(result["length_lon"], item[2]) == True)

class PayloadTestCases(TestBaseClass):
    def setUp(self):
        self.test_data = {
            "imager": {
                "fov":2.22,
                "d":0.0225,
                "f":0.58,
                "sensor":[4096,4096],
                "pixel":5.5E-6
            },
            "test_alt":500,
            "test_lat":46.1922,
            "test_lon":30.3333,
        }
        self.fp_epsilon = 0.001

    def test_calculate_swath(self):
        result = calculate_swath(self.test_data["imager"]["fov"], self.test_data["test_alt"])
        assert(self.fp_eq(result,19.375)==True)

    def test_calculate_fov(self):
        d = self.test_data["imager"]["d"]
        f = self.test_data["imager"]["f"]
        result = calculate_camera_fov(d,f)
        assert(self.fp_eq(result,2.222)==True)

    def test_calculate_gsd(self):
        p_size = self.test_data["imager"]["pixel"]
        f_len = self.test_data["imager"]["f"]
        p_alt = self.test_data["test_alt"]
        result = calculate_camera_gsd(p_alt, p_size, f_len)
        assert(self.fp_eq(result,4.741)==True)

    def test_get_imager_frame(self):
        result = get_imager_frame(
            self.test_data["imager"]["fov"],
            self.test_data["test_alt"],
            self.test_data["test_lat"],
            self.test_data["test_lon"]
        )
        assert(self.fp_eq(result["top"], 46.279) == True)
        assert(self.fp_eq(result["left"], 30.207) == True)
        assert(self.fp_eq(result["bottom"], 46.105) == True)
        assert(self.fp_eq(result["right"], 30.458) == True)

# TBD - test entire mission scenario
class MissionScenarioTest(TestCase):
    def setUp(self):
        self.norad_id = 44878
        self.start_date = {
            "year":2020,
            "month":11,
            "day": 28,
            "hour":20,
            "min": 26,
            "sec": 16
        }
        self.tle_data = {
            "line_1": "1 44878U 19092F   20351.51834954  .00001625  00000-0  87961-4 0  9991",
            "line_2": "2 44878  97.4685 171.7951 0015492  85.6297 274.6705 15.15948331 55114",
        }
        self.satellite_config = {
            "config_instruments": {
                "imager": {
                    "fov":1.6,
                    "d":0.01,
                    "f":0.5,
                    "sensor":[4096,3072],
                    "pixel":3.2E-6
                },
            }
        }
        self.scenario_data = {
            "scenario_id":1,
            "start_date":{
                "year":2020,
                "month":11,
                "day":4,
                "hour":18,
                "min":40,
                "sec": 37
            },
            "mission_name": "eo_basic",
            "description": "A basic Earth Observation mission",
                "initial_setup":{
                "norad_id":44878,
                "fp_precision":0.001
            },
            "objectives":[
                {
                    "type":"take_photo",
                    "score_points":100,
                    "definition":{
                        "top": 26.327,
                        "left": -38.374,
                        "bottom":26.198,
                        "right":-38.231,
                        "target":"Earth"
                    }
                }
            ]
        }
        self.win_time = 390

    def test_sample_scenario(self):
        env_sim = CMSE_Env()
        sat_sim = CMSE_Sat()
        sce_sim = CMSE_SceEng()
        # create scenario
        self.mission = {}
        self.mission["environment"] = env_sim.create_mission_environment(self.norad_id, self.start_date, self.tle_data)
        self.mission["satellite"] = sat_sim.create_mission_satellite(self.satellite_config)
        self.mission["scenario"] = sce_sim.initialize_scenario(self.mission, self.scenario_data)
        # run scenario
        steps = 5
        i = 0
        while i<400:
            self.mission["environment"] = env_sim.evolve_environment(self.mission["environment"], steps)
            self.mission["satellite"] = sat_sim.evolve_satellite(self.mission, steps)
            self.mission["scenario"] = sce_sim.evaluate_progress(self.mission)
            if i == self.win_time:
                self.mission = sce_sim.execute_mission_action(self.mission,"take_photo")
            i = i + steps
        assert(self.mission["scenario"]["progress"] == self.mission["scenario"]["points_to_win"])
