import time

import adafruit_ds3231  # type: ignore
import board
import busio
import digitalio


def main() -> None:
    """Main entry point."""
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    i2c = busio.I2C(board.GP1, board.GP0)
    rtc = adafruit_ds3231.DS3231(i2c)

    while True:
        led.value = not led.value
        t = rtc.datetime
        print(f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}")
        time.sleep(1.0)


main()
