"""4-display photo clock — shows HH:MM using random digit images."""

import gc
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

STUB_CS_PIN = board.GP3
RST_PIN = board.GP2
CS_PINS = [board.GP21, board.GP22, board.GP27, board.GP4]


def random_image_path(digit: int) -> str:
    """Return path to a random BMP for the given digit."""
    folder = f"/sd/{digit}"
    files = os.listdir(folder)
    return f"{folder}/{random.choice(files)}"


def send_image(spi: busio.SPI, path: str, cs: digitalio.DigitalInOut) -> None:
    """Load a BMP from SD and push it to the display selected by cs."""
    cs.value = False
    displayio.release_displays()
    bus = fourwire.FourWire(
        spi, command=board.GP5, chip_select=STUB_CS_PIN, baudrate=12_000_000
    )
    display = adafruit_ili9341.ILI9341(bus, width=320, height=240, auto_refresh=False)
    bitmap = displayio.OnDiskBitmap(path)
    group = displayio.Group()
    group.append(displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader))
    display.root_group = group
    display.refresh()
    cs.value = True
    gc.collect()


# --- Hardware init ---

displayio.release_displays()
gc.collect()

# LED
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

# Display CS pins
cs_pins: list[digitalio.DigitalInOut] = []
for pin in CS_PINS:
    cs = digitalio.DigitalInOut(pin)
    cs.direction = digitalio.Direction.OUTPUT
    cs.value = True
    cs_pins.append(cs)

# Display SPI
spi = busio.SPI(clock=board.GP6, MOSI=board.GP7)

# Reset all displays
rst = digitalio.DigitalInOut(RST_PIN)
rst.direction = digitalio.Direction.OUTPUT
rst.value = False
time.sleep(0.01)
rst.value = True
time.sleep(0.12)

# --- Main loop ---

print("Photo clock started")

prev_digits: tuple[int, ...] | None = None
while True:
    led.value = not led.value
    t = rtc.datetime
    digits = (t.tm_hour // 10, t.tm_hour % 10, t.tm_min // 10, t.tm_min % 10)
    if digits != prev_digits:
        for i, digit in enumerate(digits):
            send_image(spi, random_image_path(digit), cs_pins[i])
            print(f"Display {i}: digit {digit}")
        prev_digits = digits
        print(f"{t.tm_hour:02d}:{t.tm_min:02d}")
    time.sleep(1)
