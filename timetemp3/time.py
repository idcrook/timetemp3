#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is covered by the LICENSE file in the root of this project.

import time

import timetemp3
from timetemp3.constants import (
    DIGIT_1,
    DIGIT_2,
    DIGIT_3,
    DIGIT_4,
    SEGMENT_COLON,
    SEGMENT_AMPM,
    DEFAULT_CLOCK_HOUR_MODE_12_OR_24,
    DEFAULT_CLOCK_SHOW_AMPM,
    DEFAULT_CLOCK_DISPLAY_SLEEP_DURATION,
)


def get_time_digits(now, hour_mode=DEFAULT_CLOCK_HOUR_MODE_12_OR_24, show_ampm=DEFAULT_CLOCK_SHOW_AMPM, toggle_colon=True):
    digits = [None] * 6
    hour = now.hour
    minute = now.minute
    second = now.second
    ampm = False

    if hour_mode != 24:
        if hour > 12:  # handle 13 through 23
            hour = hour - 12
            ampm = True
        elif hour == 12:
            ampm = True
        if hour == 0:  # handle 0 (hour of midnight)
            hour = 12

    if not show_ampm:
        ampm = False

    digits[SEGMENT_AMPM] = ampm

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
        digits[SEGMENT_COLON] = second % 2
    else:
        digits[SEGMENT_COLON] = True

    return digits


def display_time_digits(
    time_digits, sleep_duration=DEFAULT_CLOCK_DISPLAY_SLEEP_DURATION, display_handle=None
):
    display = display_handle

    if display:
        #display.fill(0)
        # display.bottom_left_dot = True
        # display.top_left_dot = True
        # display.set_digit(DIGIT_1, time_digits[DIGIT_1])
        # display.set_digit(DIGIT_2, time_digits[DIGIT_2])
        # display.set_digit(DIGIT_3, time_digits[DIGIT_3])
        # display.set_digit(DIGIT_4, time_digits[DIGIT_4])
        # display.set_colon(time_digits[DIGIT_COLON])
        display[DIGIT_1] = str(time_digits[DIGIT_1])
        display[DIGIT_2] = str(time_digits[DIGIT_2])
        display[DIGIT_3] = str(time_digits[DIGIT_3])
        display[DIGIT_4] = str(time_digits[DIGIT_4])
        #display.colon = time_digits[DIGIT_COLON]
        display.colons[0] = time_digits[SEGMENT_COLON]
        display.ampm = time_digits[SEGMENT_AMPM]

        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        #display.show()

        # sleep_duration should be less than 1 second to prevent colon jittering
        time.sleep(sleep_duration)


