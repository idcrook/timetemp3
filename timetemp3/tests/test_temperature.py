from unittest import TestCase

import timetemp3

class TestOutdoorTemperatureDigits(TestCase):
    def test_is_range_10to99(self):
        digits = timetemp3.get_temperature_digits_in_fahrenheit(68.0, 'outdoor')
        self.assertEqual(digits, [6, 8, 0x6B, 'F', False])