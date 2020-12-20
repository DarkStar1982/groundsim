from django.test import TestCase
from groundsim.mse.lib_splice import (
    pack4x8to32,
    decode_prefix,
    decode_address,
    PRE_MOV_RAM
)

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
