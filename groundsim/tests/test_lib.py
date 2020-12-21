from math import radians, isclose
from django.test import TestCase
from groundsim.tests.test_core import TestBaseClass
from groundsim.mse.lib_splice import (
    pack4x8to32,
    decode_prefix,
    decode_address,
    PRE_MOV_RAM
)
from groundsim.mse.lib_astro import get_orbital_data, time_since_periapsis, calculate_degree_length

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

class SpliceTestCases(TestCase):
    def setUp(self):
        self.test_byte_values= [
            [0x00, 0x00, 0x00, 0x00],
            [0x00, 0x00, 0x00, 0xFF],
            [0x00, 0x00, 0x01, 0x00],
            [0x00, 0x00, 0x01, 0xFF],
            [0x00, 0x00, 0x02, 0x00],
            [0x00, 0x00, 0xFF, 0xFF],
            [0x00, 0x01, 0x00, 0x00],
            [0x00, 0x01, 0xFF, 0xFF],
            [0x00, 0x02, 0x00, 0x00],
            [0x00, 0xFF, 0xFF, 0xFF],
            [0x01, 0x00, 0x00, 0x00],
            [0xFF, 0xFF, 0xFF, 0xFF],
        ]
        self.test_byte_results = [
            0x00000000,
            0x000000FF,
            0x00000100,
            0x000001FF,
            0x00000200,
            0x0000FFFF,
            0x00010000,
            0x0001FFFF,
            0x00020000,
            0x00FFFFFF,
            0x01000000,
            0xFFFFFFFF
        ]
        self.test_addresses = [["0",0], ["100",100], ["255",255]]

    def test_pack8to32(self):
        i = 0
        for item in self.test_byte_values:
            result = pack4x8to32(item[0], item[1], item[2],item[3])
            assert (result==self.test_byte_results[i])
            i = i + 1

    def test_valid_decoding(self):
        result = decode_prefix("PRE_MOV_RAM")
        assert(PRE_MOV_RAM==result)

    def test_invalid_decoding(self):
        result = decode_prefix("INVALID_DATA")
        assert(-1==result)

    def test_decode_address(self):
        for item in self.test_addresses:
            assert(decode_address(item[0])==item[1])
