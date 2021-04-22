from math import radians, isclose
from django.test import TestCase
from groundsim.tests.test_core import TestBaseClass
from groundsim.mse.lib_splice import (
    pack4x8to32,
    unpack32to4x8,
    decode_symbol,
    decode_prefix,
    decode_address,
    decode_parameter,
    decode_register,
    process_code_line,
    process_program_code,
    PREFIXES,
    PARAMETERS,
    REGISTERS,
    OPCODES
)
from groundsim.mse.lib_astro import (
    get_orbital_data,
    time_since_periapsis,
    calculate_degree_length,
    compute_orbit_track
)
from groundsim.mse.lib_adcs import get_adcs_vectors

class AstroTestCases(TestBaseClass):
    def setUp(self):
        self.tle_data = {
            "line_1":'1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082',
            "line_2":'2 25544  51.6498 109.4756 0003572  55.9686 274.8005 15.49815350868473'

        }
        self.tle_data_2 = {
            "line_1":'1 25544U 98067A   21108.03584674  .00000927  00000-0  25054-4 0  9997',
            "line_2":'2 25544  51.6449 280.2435 0002643 240.0991 206.4652 15.48894052279273'

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
        assert(isclose(result,648.028,abs_tol=self.fp_epsilon)==True)

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

    def test_compute_orbit_track(self):
        start_date = {
            "year":2021,
            "month":1,
            "day":1,
            "hour":0,
            "min":0,
            "sec": 0
        }
        end_date  = {
            "year":2021,
            "month":1,
            "day":2,
            "hour":23,
            "min":59,
            "sec": 59
        }
        step = 5
        #lat = 46.11
        #lon = 30.21
        result = compute_orbit_track(self.tle_data_2, start_date, end_date, step)
        print(len(result))

# TBD!
class ADCSTestCases(TestBaseClass):
    def test_get_adcs_vectors(self):
        sat_pos = get_orbital_data(self.tle_data, self.time_data)
        result = get_adcs_vectors(self.time_data, self.tle_data)
        #print(result)

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
        self.test_param = ["P_ADC_MODE", PARAMETERS["P_ADC_MODE"]]
        self.test_register = ["FREG_U", REGISTERS["FREG_U"]]
        self.test_prefix = ["PRE_MOV_RAM", PREFIXES["PRE_MOV_RAM"]]
        self.test_program_source = [
            "1,1,10,7",
            "OP_LEA, FREG_A, 1, 1",
            "OP_LEA, FREG_B, 1, 2",
            "OP_LEA, FREG_C, 1, 3",
            "OP_FMA, FREG_A, FREG_B, FREG_C",
            "OP_MOV, PRE_MOV_RAM, FREG_C, 3",
            "OP_STR, PRE_STR_FPU, FREG_C",
            "OP_HLT",
            "1.0f",
            "2.0f",
            "1.0f"
        ]
        self.test_program_code = [
            "1010a07",
            "2100101",
            "2110102",
            "2120103",
            "9101112",
            "1021203",
            "8020012",
            "7000000",
            "3f800000",
            "40000000",
            "3f800000"
        ]
        self.test_opcodes = [
            0x01010a07,
            0x02100101,
            0x02110102,
            0x02120103,
            0x09101112,
            0x01021203,
            0x08020012,
            0x07000000,
        ]
        self.test_decoded = [
            [1,1,10,7],
            [OPCODES["OP_LEA"], REGISTERS["FREG_A"], 1, 1],
            [OPCODES["OP_LEA"], REGISTERS["FREG_B"], 1, 2],
            [OPCODES["OP_LEA"], REGISTERS["FREG_C"], 1, 3],
            [OPCODES["OP_FMA"], REGISTERS["FREG_A"], REGISTERS["FREG_B"], REGISTERS["FREG_C"]],
            [OPCODES["OP_MOV"], PREFIXES["PRE_MOV_RAM"], REGISTERS["FREG_C"], 3],
            [OPCODES["OP_STR"], PREFIXES["PRE_STR_FPU"], OPCODES["OP_NOP"], REGISTERS["FREG_C"]],
            [OPCODES["OP_HLT"], OPCODES["OP_NOP"], OPCODES["OP_NOP"], OPCODES["OP_NOP"]],
        ]

    def test_pack8to32(self):
        i = 0
        for item in self.test_byte_values:
            result = pack4x8to32(item[0], item[1], item[2],item[3])
            assert (result==self.test_byte_results[i])
            i = i + 1

    def test_unpack32to8(self):
        i = 0
        while i<len(self.test_opcodes):
            item = self.test_opcodes[i]
            result = unpack32to4x8(item)
            # print(result)
            assert (result == self.test_decoded[i])
            i = i + 1

    def test_valid_decoding(self):
        assert(decode_parameter(self.test_param[0])==self.test_param[1])
        assert(decode_prefix(self.test_prefix[0])==self.test_prefix[1])
        assert(decode_register(self.test_register[0])==self.test_register[1])

    def test_invalid_decoding(self):
        result = decode_symbol(PREFIXES, "INVALID_DATA")
        assert(-1==result)

    def test_decode_address(self):
        for item in self.test_addresses:
            assert(decode_address(item[0])==item[1])

    def test_process_line(self):
        p_mode = 0
        i = 0
        while i<len(self.test_program_source):
            result = process_code_line(self.test_program_source[i],p_mode)
            p_mode = result[0]
            output = "{:x}".format(result[1])
            assert(output == self.test_program_code[i])
            i = i + 1

    def test_process_program(self):
        result = process_program_code(self.test_program_source)
        i = 0
        while i<len(self.test_program_source):
            assert(self.test_program_code[i]==result[i])
            i = i + 1
