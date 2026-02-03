# -*- coding: utf-8 -*-

# This file is covered by the LICENSE file in the root of this project.

__author__ = "David Crook"
__copyright__ = "Copyright 2021, 2022, 2026"
__credits__ = []
__license__ = "MIT"
__version__ = "0.3.0"
__maintainer__ = "David Crook"
__email__ = "idcrook@users.noreply.github.com"
# __status__ = "Prototype", "Development", or "Production"

import Adafruit_BMP.BMP085 as BMP085
# from Adafruit_LED_Backpack import SevenSegment

import board
from adafruit_ht16k33.segments import BigSeg7x4
import adafruit_bmp280

import timetemp3
from timetemp3.constants import (
    DEFAULT_CLOCK_LED_SEGMENT_I2C_ADDRESS,
    DEFAULT_TEMPERATURE_LED_SEGMENT_I2C_ADDRESS,
    DEFAULT_TEMPERATURE_BMP_SENSOR_I2C_ADDRESS,
)

def set_display_brightness(display, brightness: float = 0.8):
    if brightness < 0.0 or brightness > 1.0:
        brightness = 0.8
    display.brightness = brightness

def initialize_and_get_time_display_handle(i2c_address=DEFAULT_CLOCK_LED_SEGMENT_I2C_ADDRESS):
    i2c = board.I2C()
    display = BigSeg7x4(i2c, address=i2c_address)

    # Clear display.
    display.fill(0)
    #display.show()
    set_display_brightness(display)

    return display


def get_temperature_sensor_handle(
        i2c_address=DEFAULT_TEMPERATURE_BMP_SENSOR_I2C_ADDRESS,
        bmp_type="bmp280"):
    if bmp_type == 'bmp280':
        i2c = board.I2C()   # uses board.SCL and board.SDA
        bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        # bmp.sea_level_pressure = 1013.25 
    else:
        bmp = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES, address=i2c_address)
    return bmp


def initialize_and_get_temperature_display_handle(
    i2c_address=DEFAULT_TEMPERATURE_LED_SEGMENT_I2C_ADDRESS,
):
    i2c = board.I2C()
    display = BigSeg7x4(i2c, address=i2c_address)

    # Clear display.
    display.fill(0)
    #display.show()
    set_display_brightness(display)

    return display
