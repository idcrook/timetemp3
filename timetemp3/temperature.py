#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is covered by the LICENSE file in the root of this project.

import time

from Adafruit_LED_Backpack import SevenSegment

import timetemp3
from timetemp3.constants import (
    DIGIT_1,
    DIGIT_2,
    DIGIT_3,
    DIGIT_4,
    DIGIT_COLON,
    DEFAULT_TEMPERATURE_LED_SEGMENT_I2C_ADDRESS,
    DEFAULT_TEMPERATURE_BMP_SENSOR_I2C_ADDRESS,
    DEFAULT_TEMPERATURE_DISPLAY_SLEEP_DURATION,
    OUTDOOR_SYMBOL_ENCODING,
    TICKMARK_SYMBOL_ENCODING,
    DEGREES_SYMBOL_ENCODING,
)

# Additional characters for 7 segment display
TEMPERATURE_RAW_DIGIT_VALUES = {
    'tickmark':        TICKMARK_SYMBOL_ENCODING,
    'outdoor_degrees': OUTDOOR_SYMBOL_ENCODING,
    '°':               DEGREES_SYMBOL_ENCODING,
}


def _lookup_where_temperature_digit(where):
    raw_value = 0x0
    if where == 'outdoor':
        raw_value = TEMPERATURE_RAW_DIGIT_VALUES['outdoor_degrees']
    elif where == 'nest':
        raw_value = TEMPERATURE_RAW_DIGIT_VALUES['°']
    else:
        raw_value = TEMPERATURE_RAW_DIGIT_VALUES['tickmark']
    return raw_value


def get_temperature_digits_in_fahrenheit(temperature, where):
    digits = [None] * 5

    if temperature is None:
        return digits

    # these are mostly constant
    digits[DIGIT_4] = 'F'
    digits[DIGIT_COLON] = False

    if round(temperature * 10.0) >= 995.0:  # 99.5 degrees or above : "###F"
        digits[DIGIT_1] = int(round(temperature) / 100)  # Hundreds
        digits[DIGIT_2] = int(round(temperature - 100.0) / 10)  # Tens
        digits[DIGIT_3] = str(int(round(temperature) % 10))  # Ones
    elif round(temperature * 10.0) > 95.0:  # 10 to 99 degrees : "##°F"
        digits[DIGIT_1] = int(round(temperature) / 10)  # Tens
        digits[DIGIT_2] = int(round(temperature) % 10)  # Ones
        digits[DIGIT_3] = _lookup_where_temperature_digit(where)
    elif round(temperature * 10.0) > -5.0:  # -0 to 9 degrees    : "_#°F"
        rounded = int(round(temperature))
        if rounded == 10:
            digits[DIGIT_1] = 1
        else:
            digits[DIGIT_1] = ' '  # Tens

        digits[DIGIT_2] = int(round(temperature) % 10)  # Ones
        digits[DIGIT_3] = _lookup_where_temperature_digit(where)
    elif round(temperature * 10.0) >= -95.0:  # -9 to 0 degrees : "-#°F"
        digits[DIGIT_1] = '-'
        digits[DIGIT_2] = int(round(abs(temperature)) % 10)  # Ones
        digits[DIGIT_3] = _lookup_where_temperature_digit(where)
    elif round(temperature * 10.0) >= -995.0:  # -99 to -10 degrees : "-##F"
        digits[DIGIT_1] = '-'  # Tens
        digits[DIGIT_2] = int(round(abs(temperature)) / 10)  # Tens
        digits[DIGIT_3] = "%01d" % (int(round(abs(temperature)) % 10))  # Ones
    else:  # error (do not expect to reach here)
        digits[DIGIT_1] = 'E'
        digits[DIGIT_2] = 'E'
        digits[DIGIT_3] = 'E'
        digits[DIGIT_4] = 'E'
        digits[DIGIT_COLON] = True

    return digits


def display_temperature_digits(
    temperature_digits,
    sleep_duration=DEFAULT_TEMPERATURE_DISPLAY_SLEEP_DURATION,
    display_handle=None,
):
    segment = display_handle

    if segment:
        segment.clear()

        segment.set_digit(DIGIT_1, temperature_digits[DIGIT_1])
        segment.set_digit(DIGIT_2, temperature_digits[DIGIT_2])
        if isinstance(temperature_digits[DIGIT_3], int):
            segment.set_digit_raw(DIGIT_3, temperature_digits[DIGIT_3])
        else:
            segment.set_digit(DIGIT_3, temperature_digits[DIGIT_3])

        segment.set_digit(DIGIT_4, temperature_digits[DIGIT_4])
        segment.set_colon(temperature_digits[DIGIT_COLON])

        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        segment.write_display()

        # sleep_duration should be less than 1 second to prevent colon jittering
        time.sleep(sleep_duration)
