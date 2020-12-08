from django.test import TestCase
from groundsim.mse.aux_astro import get_orbital_data
from skyfield.api import EarthSatellite, load

class AstroTestCases(TestCase):
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

    def test_get_orbital_data(self):
        result = get_orbital_data(self.tle_data, self.time_data)
        assert(result["lat"] == 50.243719934523405)
        assert(result["lng"] == -86.38981073049757)
        assert(result["alt"] == 420.87416164082754)
        assert(result["gcrs_vector"][0] == -3918.8765203043263)
        assert(result["gcrs_vector"][1] == -1887.648325397842)
        assert(result["gcrs_vector"][2] == 5209.0880257350755)
        assert(result["sunlit"] == False)
        assert(result["elements"].semi_major_axis.km == 6790.296966934996)
        assert(result["elements"].eccentricity == 0.0007679723906870147)
        assert(result["elements"].inclination.degrees == 51.71022207752498)
        assert(result["elements"].longitude_of_ascending_node.degrees == 96.70139840607773)
        assert(result["elements"].argument_of_periapsis.degrees == 60.16124202960846)
        assert(result["elements"].true_anomaly.degrees == 41.89455357025001)
