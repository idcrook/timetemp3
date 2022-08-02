#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is covered by the LICENSE file in the root of this project.

import logging
import json

from pprint import pformat
import requests  # so can handle exceptions

import timetemp3
from timetemp3.temperature import (
    get_temperature_digits_in_fahrenheit,
    display_temperature_digits,
)

from phant3.Phant import Phant

# these are for debug output, not data logging
logger = logging.getLogger('weather_logger')
# VERBOSITY = logging.INFO  # set to logging.DEBUG for more verbose
# logger.setLevel(VERBOSITY)


def create_phant_obj(phant_config_json = 'phant-config.example.json'):
    # Read in Phant feed config file
    phant_obj = Phant(jsonPath=phant_config_json)
    try:
        logger.info(pformat(phant_obj.stats))
    except json.decoder.JSONDecodeError as je:
        logger.error("Phant API error: %s" % je)
        raise
    except requests.exceptions.ConnectionError as ce:
        logger.error("Phant API error: %s" % ce)
        raise
    else: 
        return phant_obj


def display_location_temperature(location, readings = None, segment = None):
    temperature_in_F = readings[location]
    temperature_digits = get_temperature_digits_in_fahrenheit(
        temperature_in_F, location
    )
    try:
        display_temperature_digits(temperature_digits, display_handle=segment)
    except IOError:
        pass


