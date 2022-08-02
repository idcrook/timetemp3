#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# magic numbers for storing / passing time digits
DIGIT_1 = 0
DIGIT_2 = 1
DIGIT_3 = 2
DIGIT_4 = 3
DIGIT_COLON = 4

# Default to 12 or 24 hour mode
DEFAULT_CLOCK_HOUR_MODE_12_OR_24 = 12

# Default number of seconds to wait after display is written
DEFAULT_CLOCK_DISPLAY_SLEEP_DURATION = 1 / 4

# Default number of seconds to wait after display is written
DEFAULT_TEMPERATURE_DISPLAY_SLEEP_DURATION = 1 / 1000

# I2C address of time display
DEFAULT_CLOCK_LED_SEGMENT_I2C_ADDRESS = 0x70
# 0x70 == 112

# Default I2C address of temperature display
DEFAULT_TEMPERATURE_LED_SEGMENT_I2C_ADDRESS = 0x71

# Default I2C address of DMP sensor display
DEFAULT_TEMPERATURE_BMP_SENSOR_I2C_ADDRESS = 0x77

# for additional seven segment characters
OUTDOOR_SYMBOL_ENCODING =  0x6B
TICKMARK_SYMBOL_ENCODING =  0x02
DEGREES_SYMBOL_ENCODING =  0x63
