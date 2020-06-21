#!/usr/bin/env python3

# This file is covered by the LICENSING file in the root of this project.

import time
import datetime
import os
import signal
from sys import exit

from timetemp3 import (
    initialize_and_get_time_display_handle,
    get_time_digits,
    display_time_digits,
)

# To run: python3 ./my_7segment_clock.py

# Set to 12 or 24 hour mode
HOUR_MODE_12_OR_24 = 12

# I2C address of display
LED_SEGMENT_I2C_ADDRESS = 0x70
# LED_SEGMENT_I2C_ADDRESS = 0x71

# Number of seconds to wait after display is written
DISPLAY_SLEEP_DURATION = 1 / 4

io_error_count = 0


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
    global io_error_count

    import logging
    logger = logging.getLogger('7_segment_clock')
    VERBOSITY = logging.INFO # set to DEBUG for more verbose
    logger.setLevel(VERBOSITY) 

    # systemd v232 INVOCATION_ID environment variable. You can check if that’s set or not.
    INVOCATION_ID = os.getenv('INVOCATION_ID')
    if INVOCATION_ID is not None:
        from systemd import journal
        jH = journal.JournalHandler()
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

    # Initialize LED display
    segment = initialize_and_get_time_display_handle(i2c_address=LED_SEGMENT_I2C_ADDRESS)
    try:
        logger.info("Using clock display I2C address: 0x%02x" % (segment._device._address,))
    except:
        pass

    def graceful_exit():
        # Turn off LED
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
            clock_digits = get_time_digits(now=now)
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
            io_error_count += 1
            print("Caught ", io_error_count, "IOErrors")
            time.sleep(2)

    graceful_exit()


# added in case script is run directly
if __name__ == '__main__':
    
    main()
