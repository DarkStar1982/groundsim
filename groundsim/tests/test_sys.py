from groundsim.tests.test_core import TestBaseClass
from groundsim.mse.sys_payload import calculate_camera_gsd, calculate_camera_fov, calculate_swath, get_imager_frame
from math import radians, isclose

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
