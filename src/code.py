import os
import random
import time

import adafruit_ds3231
import adafruit_ili9341
import board
import busio
import digitalio
import displayio
import fourwire
import sdcardio
import storage


def random_image_path(digit: int) -> str:
    """Return path to a random BMP for the given digit."""
    folder = f"/sd/{digit}"
    files = os.listdir(folder)
    return f"{folder}/{random.choice(files)}"


def main() -> None:
    """Main entry point."""
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    # RTC
    i2c = busio.I2C(board.GP1, board.GP0)
    rtc = adafruit_ds3231.DS3231(i2c)

    # SD card
    sd_spi = busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=board.GP12)
    sd = sdcardio.SDCard(sd_spi, board.GP13)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")

    # Display
    displayio.release_displays()
    disp_spi = busio.SPI(clock=board.GP6, MOSI=board.GP7)
    display_bus = fourwire.FourWire(disp_spi, command=board.GP5, chip_select=board.GP4)
    display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

    group = displayio.Group()
    display.root_group = group

    prev_sec = -1
    while True:
        led.value = not led.value
        t = rtc.datetime
        sec = t.tm_sec
        if sec != prev_sec:
            prev_sec = sec
            digit = sec % 10
            path = random_image_path(digit)
            bitmap = displayio.OnDiskBitmap(path)
            while len(group):
                group.pop()
            group.append(displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader))
            print(f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d} -> {path}")
        time.sleep(0.1)


main()
