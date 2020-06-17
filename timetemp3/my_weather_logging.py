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
import pathlib
from pprint import pprint
import signal
import ssl
from threading import Event
import requests  # so can handle exceptions

from timetemp3 import (
    get_temperature_sensor_handle,
    initialize_and_get_temperature_display_handle,
    get_temperature_digits_in_fahrenheit,
    display_temperature_digits,
)

from phant3.Phant import Phant

# FIXME: Refactor into timetemp3/__init__.py
import nest  # https://github.com/jkoelker/python-nest/
from pyowm.owm import OWM  # https://github.com/csparpa/pyowm
from pyowm.commons import exceptions as OwmExceptions

usage = """
    script app_config_json phant_config_json
"""

# Logging sensor readings to Phant
LOGGING = True
# LOGGING = False
LOGGING_COUNT = 0
# borrowed field names from previous project
LOGGING_DATA = {}
LOGGING_FIELDS = ("cloudiness",
                  "cond",
                  "cond_desc",
                  "dew_point",
                  "dt",
                  "in_humid",
                  "in_pres",
                  "in_tc",
                  "in_tf",
                  "out_feels_like",
                  "out_humid",
                  "out_pres",
                  "out_temp",
                  "uvi",
                  "weather_code",
                  "weather_icon_name",
                  "wind_deg",
                  "wind_speed",)

# How long to wait (in seconds) between uploading measurements.
LOGGING_PERIOD_SECONDS = 5 * 60

PREVIOUS_UPLOAD_TIME = None

# Approximately how often sensor measurements are made (in seconds)
SENSOR_MEASUREMENT_INTERVAL = 15


# Default time to wait before hitting API again.
WEBAPI_PERIOD_SECONDS = 5 * 60

# Use Open Weather Map API for local weather - https://openweathermap.org/api https://openweathermap.org/api/one-call-api
OWM_API = True
# OWM_API = False
OWM_REFRESH_INTERVAL = WEBAPI_PERIOD_SECONDS

# Use Nest API for another indoor temperature source
NEST_API = True
# NEST_API = False
NEST_REFRESH_INTERVAL = WEBAPI_PERIOD_SECONDS

# How long to wait (in seconds) between temperature locations
ALTERNATE_TEMPERATURE_DISPLAY_SECONDS = 5
ALTERNATE_TEMPERATURE_LOCATIONS = ('sensor', 'outdoor', 'nest')
UPDATE_LOCATION_INTERVALS = (
    SENSOR_MEASUREMENT_INTERVAL, OWM_REFRESH_INTERVAL, NEST_REFRESH_INTERVAL, )
UPDATE_PREVIOUS_TIMES = [None] * len(ALTERNATE_TEMPERATURE_LOCATIONS)

# Initalize recordkeeping for updates
UPDATE_CYCLE_NUMBERS = [-1 for i in range(
    len(ALTERNATE_TEMPERATURE_LOCATIONS))]
# Use -1 to represent that update is always requests if not yet initialized

BMP_ADDRESS = 0x77
LED_DISPLAY_ADDRESS = 0x71
DISPLAY_SLEEP_DURATION = 1 / 100
# VERBOSE_BMP_READINGS = True
VERBOSE_BMP_READINGS = False

UNINITIALIZED_READING = -100.0
RECENT_READINGS = {ALTERNATE_TEMPERATURE_LOCATIONS[0]: UNINITIALIZED_READING,
                   ALTERNATE_TEMPERATURE_LOCATIONS[1]: UNINITIALIZED_READING,
                   ALTERNATE_TEMPERATURE_LOCATIONS[2]: UNINITIALIZED_READING,
                   }

try:
    app_config_json = sys.argv[1]
    phant_config_json = sys.argv[2]
except:
    print(usage)
    sys.exit(1)

print(app_config_json)
print(phant_config_json)


def convert_json_string_to_hexadecimal_value(s):
    value = 0
    try:
        value = int(s, 16)
    except:
        pass
    return value


# Read in config file
with open(app_config_json) as config_file:
    config = json.loads(config_file.read())
# pprint(config)
pprint(config["i2c_addresses"])

bmp_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["bmp085"]
) or BMP_ADDRESS
led_display_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["i2c_led"]
) or LED_DISPLAY_ADDRESS

owm_secret_key = config["owm"]["secret-key"]
owm_lat = config["owm"]["lat"]
owm_lon = config["owm"]["lon"]

nest_client_id = config['timetemp_nest']['client_id']
nest_client_secret = config['timetemp_nest']['client_secret']
# FIXME: more rrobustly form/check path
nest_access_token_cache_file = 'nest.json'

# Create display instance
segment = initialize_and_get_temperature_display_handle(
    i2c_address=led_display_address)

# Create sensor instance
bmp = get_temperature_sensor_handle(i2c_address=bmp_address)

print(pathlib.Path().absolute())

if LOGGING:
    # Read in Phant config file
    phant_obj = Phant(jsonPath=phant_config_json)
    print(
        'Logging sensor measurements taken every {2} seconds \
        to "{0}" every {1} seconds.'.format(
            phant_obj.title, LOGGING_PERIOD_SECONDS, SENSOR_MEASUREMENT_INTERVAL
        )
    )
    # print(phant_obj)

# Initialize 'NAPI' and 'nest_temperature'
global NAPI
NAPI = None
if NEST_API:
    nest_temperature = 35.0
    NAPI = nest.Nest(
        client_id=nest_client_id,
        client_secret=nest_client_secret,
        access_token_cache_file=nest_access_token_cache_file,
    )
    try:
        if NAPI.authorization_required:
            print('Authorization required.  Run "python3 ./nest_access.py"')
            raise SystemExit

        for structure in NAPI.structures:
            print('Structure %s' % structure.name)
            print('    Away: %s' % structure.away)
            print('    Devices:')

            for device in structure.thermostats:
                print('        Device: %s' % device.name)
                print('            Temp: %0.1f' % device.temperature)
                nest_temperature = device.temperature
    except requests.exceptions.ConnectionError as errec:
        print("Nest API: Error Connecting:", errec)
        print('-W- Is network down?')
        # log_error(error_type='OWM API: ConnectionError')
    finally:
        # disable API if a network error encountered
        if nest_temperature == 35.0:
            NEST_API = False

print("Nest API enabled:", NEST_API)

if OWM_API:
    outside_temperature = 42
    owm = OWM(owm_secret_key)
    mgr = owm.weather_manager()
    try:
        one_call = mgr.one_call(owm_lat, owm_lon)
        currently = one_call.current
        print(currently.status)
        print(currently.detailed_status)
        print(currently.reference_time())
        print(currently.temperature(unit='fahrenheit'))
    except requests.exceptions.ConnectionError as errec:
        print("OWM API: Error Connecting:", errec)
        print('-W- Is network down?')
    except OwmExceptions.APIRequestError as errapi:
        print("OWM API Error:", errapi)
    finally:
        # disable API if a network error encountered
        if not currently:
            OWM_API = False

print("OWM API enabled:", OWM_API)


ALTERNATE_TEMPERATURE_LOCATION_ENABLES = (True, OWM_API, NEST_API)

# via https://stackoverflow.com/a/46346184/47850
exit_sentinel = Event()


def exit_gracefully(signum, frame):
    print("Received signal " + str(signum) + " on line " +
          str(frame.f_lineno) + " in " + frame.f_code.co_filename)
    exit_sentinel.set()


def is_location_enabled(location):
    location_index = ALTERNATE_TEMPERATURE_LOCATIONS.index(location)
    return ALTERNATE_TEMPERATURE_LOCATION_ENABLES[location_index]


def is_time_to_update(start_time, location='sensor'):
    if not is_location_enabled(location):
        return False

    if RECENT_READINGS[location] == UNINITIALIZED_READING:
        return True

    location_index = ALTERNATE_TEMPERATURE_LOCATIONS.index(location)
    update_interval = UPDATE_LOCATION_INTERVALS[location_index]
    update_cycle_number = UPDATE_CYCLE_NUMBERS[location_index]
    # previous_update = UPDATE_PREVIOUS_TIMES[location_index]
    current_time = time.time()
    next_update_deadline = start_time + \
        (update_cycle_number + 1) * update_interval
    #print(location, "time until deadline", next_update_deadline - current_time)
    if current_time > next_update_deadline:
        return True

    return False


def is_time_to_upload(start_time):
    # Check that logging is enabled
    if not LOGGING:
        return False

    # Check that required data is available
    location_index_sensor = ALTERNATE_TEMPERATURE_LOCATIONS.index('sensor')
    location_index_outdoor = ALTERNATE_TEMPERATURE_LOCATIONS.index('outdoor')
    sensor_not_updated = UPDATE_PREVIOUS_TIMES[location_index_sensor] is  None
    outdoor_not_updated = UPDATE_PREVIOUS_TIMES[location_index_outdoor] is  None
    if sensor_not_updated or outdoor_not_updated:
        return False

    update_interval = LOGGING_PERIOD_SECONDS
    update_cycle_number = LOGGING_COUNT
    # previous_upload = PREVIOUS_UPLOAD_TIME
    current_time = time.time()
    next_update_deadline = start_time + (update_cycle_number) * update_interval
    #print("time until next logging", next_update_deadline - current_time)
    if current_time > next_update_deadline:
        return True
    else:
        return False


def update_location(location='sensor'):
    if location == 'sensor':
        update_location_sensor()
    elif location == 'nest':
        update_location_nest()
    elif location == 'outdoor':
        update_location_owm()


def location_updated(location):
    location_index = ALTERNATE_TEMPERATURE_LOCATIONS.index(location)
    current_time = time.time()
    # if UPDATE_PREVIOUS_TIMES[location_index]:
    #     print(location, "last updated", current_time -
    #           UPDATE_PREVIOUS_TIMES[location_index], "seconds ago")
    UPDATE_PREVIOUS_TIMES[location_index] = current_time
    UPDATE_CYCLE_NUMBERS[location_index] = UPDATE_CYCLE_NUMBERS[location_index] + 1


def update_location_nest():
    try:
        if NAPI.authorization_required:
            print(
                'Authorization required.  Run \
                "python3 ./nest_access.py"'
            )
            raise SystemExit

        for structure in NAPI.structures:
            for device in structure.thermostats:
                nest_temperature = device.temperature
                # print('Nest temperature: {0}'.format(nest_temperature))
    except requests.exceptions.ConnectionError as errec:
        print("NEST API: Error Connecting:", errec)
        print('-W- Is network down?')
        log_error(error_type='NEST API: ConnectionError')
    except IndexError as e:
        print("NEST API: IndexError:", e)
        log_error(error_type='NEST API: IndexError')
    except nest.nest.APIError as errnapi:
        print("NEST API: APIError:", errnapi)
        log_error(error_type='NEST API: APIError')

    RECENT_READINGS['nest'] = nest_temperature
    location_updated('nest')


def update_location_owm():
    try:
        one_call = mgr.one_call(owm_lat, owm_lon)
        currently = one_call.current
    except requests.exceptions.HTTPError as e:
        # Need an 404, 503, 500, 403 etc.
        status_code = e.response.status_code
        print("HTTPError:", status_code, e)
        log_error(error_type='OWM API: HTTPError')
    except requests.exceptions.ConnectionError as errec:
        print("OWM API: Error Connecting:", errec)
        print('-W- Is network down?')
        log_error(error_type='OWM API: ConnectionError')
    except OwmExceptions.APIRequestError as errapi:
        print("OWM API Error:", errapi)
        log_error(error_type='OWM API: APIRequestError')
    # print("OWM API:", end="  ")

    outside_temperature = 42
    try:
        outside_temperature = currently.temperature(unit='fahrenheit')[
            'temp'
        ]
    except:
        print("OWM: Unexpected error:", sys.exc_info()[0])
        raise

    # save values for periodic logging
    LOGGING_DATA['cloudiness'] = currently.clouds
    LOGGING_DATA['cond'] = currently.status
    LOGGING_DATA['cond_desc'] = currently.detailed_status
    LOGGING_DATA['dew_point'] = currently.dewpoint
    LOGGING_DATA['dt'] = currently.ref_time
    LOGGING_DATA['out_feels_like'] = currently.temperature(unit='fahrenheit')[
        'feels_like']
    LOGGING_DATA['out_humid'] = currently.humidity
    LOGGING_DATA['out_pres'] = currently.pressure['press']
    LOGGING_DATA['out_temp'] = outside_temperature
    LOGGING_DATA['uvi'] = currently.uvi
    LOGGING_DATA['weather_code'] = currently.weather_code
    LOGGING_DATA['weather_icon_name'] = currently.weather_icon_name
    wind = currently.wind(unit='miles_hour')
    LOGGING_DATA['wind_deg'] = wind['deg']
    LOGGING_DATA['wind_speed'] = wind['speed']

    RECENT_READINGS['outdoor'] = outside_temperature
    location_updated('outdoor')


def log_data():
    global LOGGING_COUNT, PREVIOUS_UPLOAD_TIME

    cloudiness = LOGGING_DATA['cloudiness']
    cond = LOGGING_DATA['cond']
    cond_desc = LOGGING_DATA['cond_desc']
    dew_point = LOGGING_DATA['dew_point']
    dt = LOGGING_DATA['dt']
    in_humid = LOGGING_DATA['in_humid']
    in_pres = LOGGING_DATA['in_pres']
    in_tc = LOGGING_DATA['in_tc']
    in_tf = LOGGING_DATA['in_tf']
    out_feels_like = LOGGING_DATA['out_feels_like']
    out_humid = LOGGING_DATA['out_humid']
    out_pres = LOGGING_DATA['out_pres']
    out_temp = LOGGING_DATA['out_temp']
    uvi = LOGGING_DATA['uvi']
    weather_code = LOGGING_DATA['weather_code']
    weather_icon_name = LOGGING_DATA['weather_icon_name']
    wind_deg = LOGGING_DATA['wind_deg']
    wind_speed = LOGGING_DATA['wind_speed']

    try:
        # cloudiness cond cond_desc dew_point dt in_humid
        # in_pres in_tc in_tf out_feels_like out_humid out_pres
        # out_temp uvi weather_code weather_icon_name wind_deg
        # wind_speed
        phant_obj.log(
            cloudiness,
            cond,
            cond_desc,
            dew_point,
            dt,
            in_humid,
            in_pres,
            in_tc,
            in_tf,
            out_feels_like,
            out_humid,
            out_pres,
            out_temp,
            uvi,
            weather_code,
            weather_icon_name,
            wind_deg,
            wind_speed,
        )

        print('Wrote a row to {0}'.format(phant_obj.title), end=" ")
        print((phant_obj.remaining_bytes, phant_obj.cap))
    except ValueError as errv:
        print('-E- Error logging to {}'.format(phant_obj.title))
        print('-W- Is phant server down?')
        print('ValueError: {}'.format(str(errv)))
        log_error(error_type='ValueError')
    except requests.exceptions.ConnectionError as errec:
        print("Error Connecting:", errec)
        print('-W- Is network down?')
        log_error(error_type='ConnectionError')
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        log_error(error_type='Timeout')

    except requests.exceptions.RequestException as err:
        print("Network request Error:", err)
        log_error(error_type='RequestError')

    LOGGING_COUNT = LOGGING_COUNT + 1
    current_time = time.time()
    # if PREVIOUS_UPLOAD_TIME:
    #     print("last uploaded", current_time -
    #           PREVIOUS_UPLOAD_TIME, "seconds ago")
    PREVIOUS_UPLOAD_TIME = current_time


def update_location_sensor():
    try:
        # Attempt to get sensor readings.
        temp = bmp.read_temperature()
        pressure = bmp.read_pressure()
        altitude = bmp.read_altitude()

    except IOError:
        # XXX: Handle/report IOErrors?
        pass

    temp_in_F = (temp * 9.0 / 5.0) + 32.0
    ambient_pressure = pressure / 100.0

    if VERBOSE_BMP_READINGS:
        print("BMP Sensor", end=" ")
        print("  Temp(°C): %.1f°C" % temp, end=" ")
        print("  Temp(°F): %.1f°F" % temp_in_F, end=" ")
        print("  Pressure: %.1f hPa" % ambient_pressure, end=" ")
        print("  Altitude: %.1f m" % altitude)

    # save values for periodic logging
    LOGGING_DATA['in_humid'] = 0
    LOGGING_DATA['in_pres'] = ambient_pressure
    LOGGING_DATA['in_tf'] = temp_in_F
    LOGGING_DATA['in_tc'] = temp

    RECENT_READINGS['sensor'] = temp_in_F
    location_updated('sensor')


def display_location_temperature(location):
    temperature_in_F = RECENT_READINGS[location]
    temperature_digits = get_temperature_digits_in_fahrenheit(
        temperature_in_F, location
    )
    # print(temperature_digits)
    try:
        display_temperature_digits(
            temperature_digits, display_handle=segment)
    except IOError:
        pass

ERROR_TABLES = {}

def log_error(error_type='UnknownError'):
    global ERROR_TABLES

    if error_type not in ERROR_TABLES:
        ERROR_TABLES[error_type] = 1
    else:
        ERROR_TABLES[error_type] = ERROR_TABLES[error_type] + 1

def main():
    def graceful_exit():
        # Turn off LED
        segment.clear()
        segment.write_display()
        sys.exit(0)

    # Register signal handler
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), exit_gracefully)

    # output current process id
    print("Weather logger PID is:", os.getpid())
    print("Starting main loop... Press CTRL+C to exit")
    number_of_locations = len(ALTERNATE_TEMPERATURE_LOCATIONS)
    start_time = time.time()
    display_cycle_number = -1

    while not exit_sentinel.is_set():
        display_cycle_number += 1
        current_location_index = display_cycle_number % number_of_locations
        current_location = ALTERNATE_TEMPERATURE_LOCATIONS[current_location_index]

        if is_time_to_update(start_time, current_location):
            # print("Updating", current_location)
            update_location(current_location)

        display_location_temperature(current_location)

        if is_time_to_upload(start_time):
            log_data()

        # Calculate the event net wait interval (pauses here)
        exit_sentinel.wait(max(0, start_time + ALTERNATE_TEMPERATURE_DISPLAY_SECONDS*display_cycle_number
                               - time.time()))

    graceful_exit()
