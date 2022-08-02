#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is covered by the LICENSE file in the root of this project.

DATA_LOGGING_FIELDS = (
    "cloudiness",
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
    "wind_speed",
)

# How long to wait (in seconds) between uploading measurements.
LOGGING_PERIOD_SECONDS = 5 * 60

