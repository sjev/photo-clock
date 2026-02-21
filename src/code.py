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


def init_display(
    spi: busio.SPI, cs: digitalio.DigitalInOut
) -> adafruit_ili9341.ILI9341:
    """Send ILI9341 init sequence to one display and return the last one."""
    cs.value = False
    displayio.release_displays()
    bus = fourwire.FourWire(
        spi, command=board.GP5, chip_select=STUB_CS_PIN, baudrate=12_000_000
    )
    display = adafruit_ili9341.ILI9341(bus, width=320, height=240, auto_refresh=False)
    cs.value = True
    return display


def load_image(path: str) -> displayio.Group:
    """Load a BMP from SD into a displayio Group."""
    bitmap = displayio.OnDiskBitmap(path)
    group = displayio.Group()
    group.append(displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader))
    return group


def refresh_display(
    display: adafruit_ili9341.ILI9341,
    group: displayio.Group,
    cs: digitalio.DigitalInOut,
) -> None:
    """Push a pre-loaded group to the display selected by cs."""
    display.root_group = group
    cs.value = False
    display.refresh()
    cs.value = True


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

# Init each display so it receives the ILI9341 configuration once.
# Keep the last display object for reuse (bus + controller stay valid).
display: adafruit_ili9341.ILI9341 | None = None
for cs in cs_pins:
    display = init_display(spi, cs)

# --- Main loop ---

print("Photo clock started")

assert display is not None
prev_digits: tuple[int, ...] | None = None
while True:
    t = rtc.datetime
    digits = (t.tm_hour // 10, t.tm_hour % 10, t.tm_min // 10, t.tm_min % 10)

    updates: list[tuple[int, displayio.Group]] = []
    for i, digit in enumerate(digits):
        # if prev_digits is not None and prev_digits[i] == digit:
        #    continue
        updates.append((i, load_image(random_image_path(digit))))

    for i, group in updates:
        refresh_display(display, group, cs_pins[i])
        print(f"Display {i}: digit {digits[i]}")
        led.value = not led.value

    prev_digits = digits
    print(f"{t.tm_hour:02d}:{t.tm_min:02d}")
    # time.sleep(15)
