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

class OBDHScriptTest(MissionScenarioTest):
    def setUp(self):
        super().setUp()
        self.test_filenames_b1 = [
            "/data/test_b1.splc",
            "/data/test_b2.splc",
        ]
        self.test_filenames_b2 = [
            "/data/test_b3.splc",
            "/data/test_b4b.splc",

        ]
        self.test_filenames_b3 = [
            "/data/test_b5.splc"
        ]
        self.test_filenames_c1 = [
            "/data/test_c1.splc"
        ]
        self.test_filenames_c2 = [
            "/data/test_c2.splc",
            "/data/test_c3.splc"
        ]
        self.test_filenames_c3 = [
            "/data/test_c4.splc",
        ]
        self.test_filenames_c4 = [
            "/data/test_c5.splc",
        ]
        self.test_filenames_d1 = [
            "/data/test_d1.splc"
        ]
        self.test_filenames_d2 = [
            "/data/test_d1.splc",
            "/data/test_d2.splc",
            "/data/test_d3.splc"
        ]
        self.test_filenames_d3 = [
            "/data/test_d4.splc"
        ]
        self.test_filenames_d4 = [
            "/data/test_d5.splc"
        ]


    def load_script_files(self, p_scen_engine, p_filenames):
        for item in p_filenames:
            f = open (SITE_ROOT + item, "r")
            data = f.read().split("\n")
            line_data = data[:-1]
            self.mission = p_scen_engine.load_obdh_program(self.mission, line_data)

    def init_simulator(self, p_env_sim, p_sat_sim):
        self.mission = {}
        self.mission["environment"] = p_env_sim.create_mission_environment(self.norad_id, self.start_date, self.tle_data)
        self.mission["satellite"] = p_sat_sim.create_mission_satellite(self.satellite_config)

    def run_simulator(self, p_env_sim, p_sat_sim):
        i = 0
        while i<self.total_time:
            self.mission["environment"] = p_env_sim.evolve_environment(self.mission["environment"], self.step_time)
            self.mission["satellite"] = p_sat_sim.evolve_satellite(self.mission, self.step_time)
            i = i + self.step_time

    def run_splice_scripts(self, p_list):
        # create simulation instance
        env_sim = CMSE_Env()
        sat_sim = CMSE_Sat()
        sce_sim = CMSE_SceEng()
        self.init_simulator(env_sim, sat_sim)
        # Load OBDH tasks
        self.load_script_files(sce_sim, p_list)
        # run simulation
        self.run_simulator(env_sim, sat_sim)

    def test_obdh_scripts_part_b1(self):
        # create simulation instance
        self.run_splice_scripts(self.test_filenames_b1)
        # check_results
        log_result_b1 = ['2:1:400.0', '2:1:0.0', '2:1:1', '2:1:510.9632641160709']
        log_result_b2 = ['2:2:0.0', '2:2:0.0', '2:2:0.0', '2:2:0.0', '2:2:0.0']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"]
        assert(log_result_b1==all_logs[-14:-10])
        assert(log_result_b2==all_logs[-5:])

    def test_obdh_scripts_part_b2(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_b2)
        # check_results
        test_result = ['2:3:300.0', '2:4:0', '2:4:1', '2:4:2', '2:4:3', '2:4:4', '2:4:5']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"]
        assert(all_logs==test_result)

    def test_obdh_scripts_part_b3(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_b3)
        # check_results
        test_result = ['2:5:0.0', '2:5:0.0', '2:5:0.0', '2:5:0.0', '2:5:0.0']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][-5:]
        assert(all_logs==test_result)

    def test_obdh_scripts_part_c1(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_c1)
        # check_results
        test_result = ['3:1:-0.034843794085361424', '3:1:510.99810791015625', '3:1:510.9632641160709']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"] [-3:]
        assert(all_logs==test_result)

    def test_obdh_scripts_part_c2(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_c2)
        # check_results
        test_result = ['3:2:2.0', '3:2:4.0', '3:2:7.0', '3:2:10.0', '3:3:2.0', '3:3:7.0', '3:3:4.0', '3:3:10.0']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][-8:]
        assert(all_logs==test_result)

    def test_obdh_scripts_part_c3(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_c3)
        test_result = ['3:4:5738.825492406754']
        # check_results
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][-1:]
        assert(all_logs==test_result)

    def test_obdh_scripts_part_c4(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_c4)
        # check_results
        test_result = ['3:5:51.61953205370378', '3:5:-0.007907162709159365']
        logs_1 = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][2:3]
        logs_2 = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][-1:]
        all_logs = logs_1+logs_2
        assert(all_logs==test_result)

    def test_obdh_scripts_part_d1(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_d1)
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][:1]
        test_result = ['4:1:516.2841926036398']
        assert(test_result == all_logs)

    def test_obdh_scripts_part_d2(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_d2)
        # check_results
        test_result = ['4:2:510.99811734794736', '4:3:0.005145685700184178']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][-4:-2]
        assert(test_result == all_logs)

    def test_obdh_scripts_part_d3(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_d3)
        # check_results
        test_result = ['4:4:4.14159', '4:4:2.71828']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][-2:]
        assert(test_result == all_logs)

    def test_obdh_scripts_part_d4(self):
        # run simulation
        self.run_splice_scripts(self.test_filenames_d4)
        # check_results
        test_result = ['4:5:0', '4:5:2010501', '4:5:4070401', '4:5:1']
        all_logs = self.mission["satellite"]["subsystems"]["obdh"]["splice_vm"]["VBUS"]["INST_LOGS"]["OUT"][-4:]
        assert(test_result == all_logs)
