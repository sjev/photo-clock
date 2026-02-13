"""Test DS3231 RTC over I2C on RP2040."""

import time

import adafruit_ds3231
import board
import busio

i2c = busio.I2C(board.GP1, board.GP0)
rtc = adafruit_ds3231.DS3231(i2c)

# Uncomment to set the time once, then re-comment and re-upload:
# import struct
# rtc.datetime = time.struct_time((2026, 2, 13, 18, 30, 0, 3, 44, -1))

while True:
    t = rtc.datetime
    print(f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}")
    time.sleep(1)
