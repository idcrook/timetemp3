# -*- coding: utf-8 -*-

import time

import Adafruit_BMP.BMP085 as BMP085
from Adafruit_LED_Backpack import SevenSegment

from phant3.Phant import Phant

import nest  # https://github.com/jkoelker/python-nest/
from pyowm.owm import OWM  # https://github.com/csparpa/pyowm
from pyowm.commons import exceptions as OwmExceptions


# magic numbers for storing / passing time digits
DIGIT_1 = 0
DIGIT_2 = 1
DIGIT_3 = 2
DIGIT_4 = 3
DIGIT_COLON = 4

# Default I2C address of clock display
CLOCK_LED_SEGMENT_I2C_ADDRESS = 0x70

# Default I2C address of temperature display
TEMPERATURE_LED_SEGMENT_I2C_ADDRESS = 0x71

# Default I2C address of DMP sensor display
TEMPERATURE_BMP_SENSOR_I2C_ADDRESS = 0x77

# Default to 12 or 24 hour mode
CLOCK_HOUR_MODE_12_OR_24 = 12

# Default number of seconds to wait after display is written
CLOCK_DISPLAY_SLEEP_DURATION = 1/4
TEMPERATURE_DISPLAY_SLEEP_DURATION = 1/1000

# Additional characters for 7 segment display
TEMPERATURE_RAW_DIGIT_VALUES = {
    'tickmark': 0x02,
    'outdoor_degrees': 0x6B,
    '°': 0x63,
}


def initialize_and_get_time_display_handle(i2c_address=CLOCK_LED_SEGMENT_I2C_ADDRESS):
    segment = SevenSegment.SevenSegment(address=i2c_address)
    # Initialize display. Must be called once before using the display.
    segment.begin()
    print("Using clock display I2C address: 0x%02x" % (i2c_address,))
    # print(segment)
    return segment


def get_time_digits(now, hour_mode=CLOCK_HOUR_MODE_12_OR_24, toggle_colon=True):
    digits = [None] * 5
    hour = now.hour
    minute = now.minute
    second = now.second

    if hour_mode != 24:
        if hour > 12:  # handle 13 through 23
            hour = hour - 12
        if hour == 0:  # handle 0 (hour of midnight)
            hour = 12

    # Set hours digits
    if hour >= 10 or hour == 0:  # Tens
        digits[DIGIT_1] = int(hour / 10)
    else:
        digits[DIGIT_1] = ' '

    digits[DIGIT_2] = hour % 10  # Ones

    # Set minutes digits
    digits[DIGIT_3] = int(minute / 10)  # Tens
    digits[DIGIT_4] = minute % 10  # Ones

    # Toggle colon
    if toggle_colon:
        # Toggle colon at 0.5 Hz (every other second)
        digits[DIGIT_COLON] = second % 2
    else:
        digits[DIGIT_COLON] = True

    return digits


def display_time_digits(time_digits, sleep_duration=CLOCK_DISPLAY_SLEEP_DURATION, display_handle=None):
    segment = display_handle

    if segment:
        segment.clear()

        segment.set_digit(DIGIT_1, time_digits[DIGIT_1])
        segment.set_digit(DIGIT_2, time_digits[DIGIT_2])
        segment.set_digit(DIGIT_3, time_digits[DIGIT_3])
        segment.set_digit(DIGIT_4, time_digits[DIGIT_4])
        segment.set_colon(time_digits[DIGIT_COLON])

        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        segment.write_display()

        # sleep_duration should be less than 1 second to prevent colon jittering
        time.sleep(sleep_duration)

def get_temperature_sensor_handle(i2c_address=TEMPERATURE_BMP_SENSOR_I2C_ADDRESS):
    bmp = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES, address=i2c_address)
    return bmp

def initialize_and_get_temperature_display_handle(i2c_address=TEMPERATURE_LED_SEGMENT_I2C_ADDRESS):
    segment = SevenSegment.SevenSegment(address=i2c_address)
    # Initialize display. Must be called once before using the display.
    segment.begin()
    print("Using temperature display I2C address: 0x%02x" % (i2c_address,))
    return segment

def _lookup_where_temperature_digit(where):
    raw_value = 0x0
    if where == 'outdoor':
        raw_value = TEMPERATURE_RAW_DIGIT_VALUES['outdoor_degrees']
    elif where == 'nest':
        raw_value =  TEMPERATURE_RAW_DIGIT_VALUES['°']
    else:
        raw_value =  TEMPERATURE_RAW_DIGIT_VALUES['tickmark']
    return raw_value

def get_temperature_digits_in_fahrenheit(temperature, where):
    digits = [None] * 5

    # these are mostly constant
    digits[DIGIT_4] = 'F'
    digits[DIGIT_COLON] = False

    if round(temperature * 10.0) >= 1000.0:  # 100 degrees or above : "###F"
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
    elif round(temperature * 10.0) > -94.9:  # -9 to 0 degrees : "-#°F"
        digits[DIGIT_1] = '-'
        digits[DIGIT_2] = int(round(abs(temperature)) % 10)  # Ones
        digits[DIGIT_3] = _lookup_where_temperature_digit(where)
    elif round(temperature * 10.0) >= -995.0:  # -99 to -10 degrees : "-##F"
        digits[DIGIT_1] = '-'  # Tens
        digits[DIGIT_2] =  int(round(abs(temperature)) / 10)  # Tens
        digits[DIGIT_3] =  "%01d" % (int(round(abs(temperature)) % 10))  # Ones
    else:  # error (do not expect to reach here)
        digits[DIGIT_1] = 'E'
        digits[DIGIT_2] = 'E'
        digits[DIGIT_3] = 'E'
        digits[DIGIT_4] = 'E'
        digits[DIGIT_COLON] = True

    return digits


def display_temperature_digits(temperature_digits, sleep_duration=TEMPERATURE_DISPLAY_SLEEP_DURATION, display_handle=None):
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
