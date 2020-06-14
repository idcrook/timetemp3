
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  - read indoor-located pressure/temperature sensor
#    - log sensor data to a phant server
#    - log external weather data (read from Web API)

import os
import sys
import time

# import datetime
import json
from pprint import pprint
import signal
import ssl
import requests  # so can handle exceptions

from timetemp3 import get_temperature_sensor_handle, initialize_and_get_temperature_display_handle, get_temperature_digits_in_fahrenheit, display_temperature_digits
# Logging sensor readings to Phant
LOGGING = True
# LOGGING = False
LOGGING_COUNT = 0

# Use Open Weather Map API for local weather - https://openweathermap.org/api https://openweathermap.org/api/one-call-api
OWM_API = True
# OWM_API = False

# Use Nest API for another indoor temperature source
NEST_API = True
# NEST_API = False

# How long to wait (in seconds) between logging measurements.
LOGGING_PERIOD_SECONDS = 300

# How often to hit the web APIs
WEBAPI_PERIOD_SECONDS = 300

# How long to wait (in seconds) between temperature locations
ALTERNATE_TEMP_SCALE_SECONDS = 5

# Approximately how often measurements are made (in seconds)
MEASUREMENT_INTERVAL = 3 * ALTERNATE_TEMP_SCALE_SECONDS

# How seldom to upload the sensor log data, if LOGGING is on (in 
# MEASUREMENT_INTERVALs)
COUNT_INTERVAL = LOGGING_PERIOD_SECONDS / MEASUREMENT_INTERVAL

BMP_ADDRESS = 0x77
LED_DISPLAY_ADDRESS = 0x70 # 0x71
DISPLAY_SLEEP_DURATION = 1/100

# Create display instance 
segment = initialize_and_get_temperature_display_handle(i2c_address = LED_DISPLAY_ADDRESS)

# Create sensor instance 
bmp = get_temperature_sensor_handle(i2c_address = BMP_ADDRESS)

# via https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print(
            "Received signal "
            + str(signum)
            + " on line "
            + str(frame.f_lineno)
            + " in "
            + frame.f_code.co_filename
        )
        self.kill_now = True

def main():

    def graceful_exit():
        # Turn off LED 
        segment.clear()
        segment.write_display()
        exit(0)

    # output current process id
    print("My PID is:", os.getpid())
    killer = GracefulKiller()

    print("Starting main loop")
    print("Press CTRL+C to exit")
    while not killer.kill_now:
        try: 
            # Attempt to get sensor readings.
            temp = bmp.read_temperature()
            pressure = bmp.read_pressure()
            altitude = bmp.read_altitude()

            temp_in_F = (temp * 9.0 / 5.0) + 32.0
            print("BMP Sensor", end=" ")
            print("  Temp(°C): %.1f°C" % temp, end=" ")
            print("  Temp(°F): %.1f°F" % temp_in_F, end=" ")
            print("  Pressure: %.1f hPa" % (pressure / 100.0), end=" ")
            print("  Altitude: %.1f m" % altitude)

            # test1 = get_temperature_digits_in_fahrenheit(105, "nest")
            # print(test1)
            # display_temperature_digits(test1, display_handle = segment)
            # time.sleep(5)

            # test2 = get_temperature_digits_in_fahrenheit(-20, "nest")
            # print(test2)
            # display_temperature_digits(test2, display_handle = segment)
            # time.sleep(5)

            temperature_digits = get_temperature_digits_in_fahrenheit(temp_in_F, "sensor")
            # print(temperature_digits)
            display_temperature_digits(temperature_digits, display_handle = segment)

            time.sleep(15)
            
        except KeyboardInterrupt:
            graceful_exit()

    graceful_exit()