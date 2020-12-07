from django.test import TestCase
from groundsim.mse.aux_astro import get_orbital_data

class AstroTestCases(TestCase):
    def test_aux_astro(self):
        result = get_orbital_data(None, None)
        assert([] == result)
