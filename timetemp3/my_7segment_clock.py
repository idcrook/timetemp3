#!/usr/bin/env python3

# This file is covered by the LICENSE file in the root of this project.

# To run: python3 ./my_7segment_clock.py [app_config.json]

import time
import datetime
import json
import os
import signal
import sys
from sys import exit

import timetemp3
from timetemp3 import constants
from timetemp3 import (
    initialize_and_get_time_display_handle,
)
from timetemp3.time import (
    get_time_digits,
    display_time_digits,
)

# Set to 12 or 24 hour mode
DEFAULT_HOUR_MODE_12_OR_24 = constants.DEFAULT_CLOCK_HOUR_MODE_12_OR_24

# I2C address of display
DEFAULT_LED_SEGMENT_I2C_ADDRESS = constants.DEFAULT_CLOCK_LED_SEGMENT_I2C_ADDRESS

# Number of seconds to wait after display is written
DISPLAY_SLEEP_DURATION = 1 / 4

# Counter for errors encountered
IO_ERROR_COUNT = 0

# These are the variables consumed
HOUR_MODE_12_OR_24      = DEFAULT_HOUR_MODE_12_OR_24
LED_SEGMENT_I2C_ADDRESS = DEFAULT_LED_SEGMENT_I2C_ADDRESS

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
    global IO_ERROR_COUNT
    global LED_SEGMENT_I2C_ADDRESS
    global HOUR_MODE_12_OR_24

    import logging
    logger = logging.getLogger('7_segment_clock')
    VERBOSITY = logging.DEBUG # logging.INFO  # set to DEBUG for more verbose
    logger.setLevel(VERBOSITY)

    # systemd v232 INVOCATION_ID environment variable. You can check if that’s set or not.
    INVOCATION_ID = os.getenv('INVOCATION_ID')
    if INVOCATION_ID is not None:
        from systemd import journal
        jH = journal.JournalHandler(SYSLOG_IDENTIFIER="my_7segment_clock")
        jH.setLevel(VERBOSITY)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        jH.setFormatter(formatter)
        logger.addHandler(jH)
        logger.debug('INVOCATION_ID=%s' % INVOCATION_ID)
    else:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
        logger.info('Not running from systemd')

    # read in any config
    try:
        app_config_json = sys.argv[1]
        # Read in config file
        with open(app_config_json) as config_file:
            config = json.loads(config_file.read())
        LED_SEGMENT_I2C_ADDRESS = config.get('led_disp_i2c_addr', DEFAULT_LED_SEGMENT_I2C_ADDRESS)
        HOUR_MODE_12_OR_24 = config.get('hour_mode', DEFAULT_HOUR_MODE_12_OR_24)

    except:
        logger.info("No app_config.json available. Using hard-coded defaults.")

    logger.info("Config: hour_mode: {hm:d}".format(hm = HOUR_MODE_12_OR_24))
    logger.info("Config: led_disp_i2c_addr: 0x{addr:02x} ({addr:d})".format(addr = LED_SEGMENT_I2C_ADDRESS))

    # Initialize LED display
    segment = None
    try:
        segment = initialize_and_get_time_display_handle(i2c_address=LED_SEGMENT_I2C_ADDRESS)
    except FileNotFoundError as efnf:
        logger.fatal("Unable to find I2C devices: {0}".format(efnf))
        raise SystemExit
    except BaseException as err:
        logger.fatal(f"Unexpected {err=}, {type(err)=}")
        raise
    else:
        logger.info("Using clock display I2C address: 0x%02x" % (segment._device._address,))


    def graceful_exit():
        # Turn off LED
        if segment is not None:
            segment.clear()
            segment.write_display()
        exit(0)

    # output current process id
    logger.info("My PID is: %d" % os.getpid())
    killer = GracefulKiller()

    logger.info("Starting main loop -  Press CTRL+C to exit")
    while not killer.kill_now:
        # Periodically update the time on a 4 char, 7-segment display
        try:
            now = datetime.datetime.now()
            clock_digits = get_time_digits(now=now, hour_mode=HOUR_MODE_12_OR_24)
            # print(clock_digits)
            display_time_digits(
                clock_digits,
                sleep_duration=DISPLAY_SLEEP_DURATION,
                display_handle=segment,
            )

        except KeyboardInterrupt:
            graceful_exit()

        # IOError: [Errno 121] Remote I/O error would occasionally surface on Raspian stretch
        except IOError:
            IO_ERROR_COUNT += 1
            logger.warning("Caught {cnt:d} IOErrors".format(cnt=IO_ERROR_COUNT))
            time.sleep(2)

    graceful_exit()


# added in case script is run directly
if __name__ == '__main__':

    main()
