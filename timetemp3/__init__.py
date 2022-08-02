# -*- coding: utf-8 -*-

# This file is covered by the LICENSE file in the root of this project.

__author__ = "David Crook"
__copyright__ = "Copyright 2021, 2022"
__credits__ = []
__license__ = "MIT"
__version__ = "0.2.0"
__maintainer__ = "David Crook"
__email__ = "idcrook@users.noreply.github.com"
# __status__ = "Prototype", "Development", or "Production"

import Adafruit_BMP.BMP085 as BMP085
from Adafruit_LED_Backpack import SevenSegment

import timetemp3
from timetemp3.constants import (
    DEFAULT_CLOCK_LED_SEGMENT_I2C_ADDRESS,
    DEFAULT_TEMPERATURE_LED_SEGMENT_I2C_ADDRESS,
    DEFAULT_TEMPERATURE_BMP_SENSOR_I2C_ADDRESS,
)

def initialize_and_get_time_display_handle(i2c_address=DEFAULT_CLOCK_LED_SEGMENT_I2C_ADDRESS):
    segment = SevenSegment.SevenSegment(address=i2c_address)
    # Initialize display. Must be called once before using the display.
    segment.begin()
    return segment


def get_temperature_sensor_handle(i2c_address=DEFAULT_TEMPERATURE_BMP_SENSOR_I2C_ADDRESS):
    bmp = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES, address=i2c_address)
    return bmp


def initialize_and_get_temperature_display_handle(
    i2c_address=DEFAULT_TEMPERATURE_LED_SEGMENT_I2C_ADDRESS,
):
    segment = SevenSegment.SevenSegment(address=i2c_address)
    # Initialize display. Must be called once before using the display.
    segment.begin()
    return segment


