import os.path
from math import radians, isclose
from django.test import TestCase
from skyfield.api import EarthSatellite, load
from groundsim.mse.core_sim import CMSE_Env, CMSE_Sat, CMSE_SceEng
from groundsim.mse.core_utils import fp_equals

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

class TestBaseClass(TestCase):
    def fp_eq(self, a, b):
        return isclose(a, b , abs_tol=self.fp_epsilon)

class UtilitiesTestCases(TestBaseClass):
    def setUp(self):
        self.a = 1.0001
        self.b = 1.0002
        self.fp_epsilon = 0.001

    def test_fp_equals(self):
        result_1 = fp_equals(self.a, self.b, self.fp_epsilon)
        result_2 = self.fp_eq(self.a, self.b)
        assert(result_1==result_2)

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
        self.total_time = 400
        self.step_time = 5
        self.test_filenames_b1 = [
            "/data/test_b1.splc",
            "/data/test_b2.splc",
        ]
        self.test_filenames_b2 = [
            "/data/test_b3.splc",
            "/data/test_b4b.splc",
            #"/data/test_b4b.splc",
            #"/data/test_b5.splc",
        ]
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
        i = 0
        while i<self.total_time:
            self.mission["environment"] = env_sim.evolve_environment(self.mission["environment"], self.step_time)
            self.mission["satellite"] = sat_sim.evolve_satellite(self.mission, self.step_time)
            self.mission["scenario"] = sce_sim.evaluate_progress(self.mission)
            if i == self.win_time:
                self.mission = sce_sim.execute_mission_action(self.mission,"take_photo")
            i = i + self.step_time
        assert(self.mission["scenario"]["progress"] == self.mission["scenario"]["points_to_win"])

    def test_obdh_scripts_part_b1(self):
        # create simulation instance
        env_sim = CMSE_Env()
        sat_sim = CMSE_Sat()
        sce_sim = CMSE_SceEng()
        self.mission = {}
        self.mission["environment"] = env_sim.create_mission_environment(self.norad_id, self.start_date, self.tle_data)
        self.mission["satellite"] = sat_sim.create_mission_satellite(self.satellite_config)
        # Load OBDH tasks
        for item in self.test_filenames_b1:
            f = open (SITE_ROOT + item, "r")
            data = f.read().split("\n")
            line_data = data[:-1]
            self.mission = sce_sim.load_obdh_program(self.mission, line_data)
        i = 0
        # run simulation
        while i<self.total_time:
            self.mission["environment"] = env_sim.evolve_environment(self.mission["environment"], self.step_time)
            self.mission["satellite"] = sat_sim.evolve_satellite(self.mission, self.step_time)
            i = i + self.step_time
        log_result_b1 = ['2:1:400.0', '2:1:0.0', '2:1:1', '2:1:510.9632641160709']
        log_result_b2 = ['2:2:0.0', '2:2:0.0', '2:2:0.0', '2:2:0.0', '2:2:0.0']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"]
        assert(log_result_b1==all_logs[-14:-10])
        assert(log_result_b2==all_logs[-5:])

    def test_obdh_scripts_part_b2(self):
        # create simulation instance
        env_sim = CMSE_Env()
        sat_sim = CMSE_Sat()
        sce_sim = CMSE_SceEng()
        self.mission = {}
        self.mission["environment"] = env_sim.create_mission_environment(self.norad_id, self.start_date, self.tle_data)
        self.mission["satellite"] = sat_sim.create_mission_satellite(self.satellite_config)
        # Load OBDH tasks
        for item in self.test_filenames_b2:
            f = open (SITE_ROOT + item, "r")
            data = f.read().split("\n")
            line_data = data[:-1]
            self.mission = sce_sim.load_obdh_program(self.mission, line_data)
        i = 0
        while i<self.total_time:
            self.mission["environment"] = env_sim.evolve_environment(self.mission["environment"], self.step_time)
            self.mission["satellite"] = sat_sim.evolve_satellite(self.mission, self.step_time)
            i = i + self.step_time
        test_result = ['2:3:300.0', '2:4:0', '2:4:1', '2:4:2', '2:4:3', '2:4:4', '2:4:5']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"]
        assert(all_logs==test_result)
