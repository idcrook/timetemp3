
import time

from Adafruit_LED_Backpack import SevenSegment

# magic numbers for storing / passing time digits
DIGIT_1 = 0
DIGIT_2 = 1
DIGIT_3 = 2
DIGIT_4 = 3
DIGIT_COLON = 4

# Default to 12 or 24 hour mode
CLOCK_HOUR_MODE_12_OR_24 = 12

# Default I2C address of display
CLOCK_LED_SEGMENT_I2C_ADDRESS = 0x70

# Default number of seconds to wait after display is written
CLOCK_DISPLAY_SLEEP_DURATION = 1/4 

def get_time_digits( now, hour_mode = CLOCK_HOUR_MODE_12_OR_24, toggle_colon = True):
    digits = [None] * 5
    hour = now.hour
    minute = now.minute
    second = now.second

    if hour_mode != 24:
        if hour > 12:  # handle 13 through 23
            hour = hour - 12
        if hour == 0:  # handle 0 (hour of midnight)
            hour = 12

    # Set hours digits
    if hour >= 10 or hour == 0:  # Tens
        digits[DIGIT_1] = int(hour / 10)
    else:
        digits[DIGIT_1] = ' '

    digits[DIGIT_2] = hour % 10 # Ones

    # Set minutes digits
    digits[DIGIT_3] = int(minute / 10)  # Tens
    digits[DIGIT_4] = minute % 10  # Ones

    # Toggle colon
    if toggle_colon:
        digits[DIGIT_COLON] = second % 2 # Toggle colon at 0.5 Hz (every other second)
    else:
        digits[DIGIT_COLON] = True

    return digits


def initialize_and_get_time_display_handle (i2c_address = CLOCK_LED_SEGMENT_I2C_ADDRESS):
    segment = SevenSegment.SevenSegment(address=i2c_address)
    # Initialize display. Must be called once before using the display.
    segment.begin()
    print("Using clock display I2C address: 0x%02x" % (i2c_address,))
    return segment

def display_time_digits(time_digits, sleep_duration = CLOCK_DISPLAY_SLEEP_DURATION, display_handle = None):
    segment = display_handle

    if segment:
        segment.clear()

        segment.set_digit(DIGIT_1, time_digits[DIGIT_1])
        segment.set_digit(DIGIT_2, time_digits[DIGIT_2])
        segment.set_digit(DIGIT_3, time_digits[DIGIT_3])
        segment.set_digit(DIGIT_4, time_digits[DIGIT_4])
        segment.set_colon(time_digits[DIGIT_COLON] )

        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        segment.write_display()

        # sleep_duration should be less than 1 second to prevent colon jittering
        time.sleep(sleep_duration)

