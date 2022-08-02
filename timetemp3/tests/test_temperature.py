from unittest import TestCase

import timetemp3
from timetemp3 import temperature
from timetemp3.constants import (
    DIGIT_1,
    DIGIT_2,
    DIGIT_3,
    DIGIT_4,
    DIGIT_COLON,
    OUTDOOR_SYMBOL_ENCODING,
    TICKMARK_SYMBOL_ENCODING,
    DEGREES_SYMBOL_ENCODING,
)


class TestTemperatureDigits(TestCase):

    def test_is_range_100_above(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(101.0, 'outdoor')
        self.assertEqual(digits, [1, 0, '1', 'F', False])

    def test_is_range_p100(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(100.0, 'outdoor')
        self.assertEqual(digits, [1, 0, '0', 'F', False])

    def test_is_range_p99p9(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(99.9, 'outdoor')
        self.assertEqual(digits, [1, 0, '0', 'F', False])
    
    def test_is_range_p99p5(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(99.5, 'outdoor')
        self.assertEqual(digits, [1, 0, '0', 'F', False])
    
    def test_is_range_p10_to_p99(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(68.0, 'nest')
        self.assertEqual(digits, [6, 8, DEGREES_SYMBOL_ENCODING, 'F', False])

    def test_is_p10(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(10.0, 'outdoor')
        self.assertEqual(digits, [1, 0, OUTDOOR_SYMBOL_ENCODING, 'F', False])

    def test_is_p09p9(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(9.9, 'outdoor')
        self.assertEqual(digits, [1, 0, OUTDOOR_SYMBOL_ENCODING, 'F', False])

    def test_is_range_n0_to_p9_A(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-0.1, 'sensor')
        self.assertEqual(digits, [' ', 0, TICKMARK_SYMBOL_ENCODING, 'F', False])

    def test_is_range_n0_to_p9_B(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(9.4, 'outdoor')
        self.assertEqual(digits, [' ', 9, OUTDOOR_SYMBOL_ENCODING, 'F', False])

    def test_is_range_n9_to_n0_A(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-0.55, 'outdoor')
        self.assertEqual(digits, ['-', 1, OUTDOOR_SYMBOL_ENCODING, 'F', False])

    def test_is_range_n9_to_n0_B(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-9.4, 'outdoor')
        self.assertEqual(digits, ['-', 9, OUTDOOR_SYMBOL_ENCODING, 'F', False])

    def test_is_range_n9_to_n0_C(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-4.35, 'outdoor')
        self.assertEqual(digits, ['-', 4, OUTDOOR_SYMBOL_ENCODING, 'F', False])

    def test_is_range_n9_to_n0_D(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-9.49, 'outdoor')
        self.assertEqual(digits, ['-', 9, OUTDOOR_SYMBOL_ENCODING, 'F', False])

    def test_is_range_n99_to_n10_A(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-10.0, 'outdoor')
        self.assertEqual(digits, ['-', 1, '0', 'F', False])

    def test_is_range_n99_to_n10_B(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-21.0, 'outdoor')
        self.assertEqual(digits, ['-', 2, '1', 'F', False])

    def test_is_range_n99_to_n10_C(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-99.49, 'outdoor')
        self.assertEqual(digits, ['-', 9, '9', 'F', False])

    def test_is_out_of_range(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(-100.0, 'outdoor')
        self.assertEqual(digits, ['E', 'E', 'E', 'E', True])

    def test_invalid_input_None(self):
        digits = temperature.get_temperature_digits_in_fahrenheit(None, 'outdoor')
        self.assertEqual(digits, [None] * 5)