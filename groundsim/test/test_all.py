from django.test import TestCase
from math import radians, isclose
from groundsim.mse.aux_astro import get_orbital_data, time_since_periapsis, calculate_degree_length
from groundsim.mse.sys_payload import calculate_swath, get_imager_frame

from skyfield.api import EarthSatellite, load

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
                "theta":1.6,
                "f":0.58,
                "sensor":[9344,7000],
                "pixel":3.2E-6
            },
            "test_alt":500,
            "test_lat":46.1922,
            "test_lon":30.3333,
        }
        self.fp_epsilon = 0.001

    def test_calculate_resolution(self):
        result = calculate_swath(self.test_data["imager"]["theta"], self.test_data["test_alt"])
        assert(self.fp_eq(result,13.963)==True)

    def test_get_imager_frame(self):
        result = get_imager_frame(
            self.test_data["imager"]["theta"],
            self.test_data["test_alt"],
            self.test_data["test_lat"],
            self.test_data["test_lon"]
        )
        assert(self.fp_eq(result["top"], 46.255) == True)
        assert(self.fp_eq(result["left"], 30.243) == True)
        assert(self.fp_eq(result["bottom"], 46.129) == True)
        assert(self.fp_eq(result["right"], 30.423) == True)
