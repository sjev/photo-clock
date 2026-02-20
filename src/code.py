"""Check all 4 ILI9341 displays — shows 'Display N' on each."""

import gc

import adafruit_ili9341
import board
import busio
import digitalio
import displayio
import fourwire
import terminalio
from adafruit_display_text import label

# GP3 is used as a stub CS for FourWire — not connected to anything.
# All 4 display CS pins (including GP4 for Display 0) are controlled manually,
# so FourWire's own CS toggle never accidentally selects a display.
STUB_CS_PIN = board.GP3
CS_PINS = [board.GP4, board.GP21, board.GP22, board.GP27]
COLORS = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00]


def make_group(text: str, color: int) -> displayio.Group:
    """Create a group with colored background and centered text."""
    group = displayio.Group()
    bg = displayio.Bitmap(320, 240, 1)
    palette = displayio.Palette(1)
    palette[0] = color
    group.append(displayio.TileGrid(bg, pixel_shader=palette))
    group.append(
        label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=100, y=120, scale=3)
    )
    return group


def send(spi, group, cs: digitalio.DigitalInOut) -> None:
    """Re-init display bus and send group to the display selected by cs."""
    cs.value = False
    displayio.release_displays()
    bus = fourwire.FourWire(
        spi, command=board.GP5, chip_select=STUB_CS_PIN, baudrate=12_000_000
    )
    display = adafruit_ili9341.ILI9341(bus, width=320, height=240, auto_refresh=False)
    display.root_group = group
    display.refresh()
    cs.value = True


# Release code.py's display bus — FourWire.deinit() calls SPI.deinit(), freeing GP6.
displayio.release_displays()
gc.collect()

cs_pins = []
for pin in CS_PINS:
    cs = digitalio.DigitalInOut(pin)
    cs.direction = digitalio.Direction.OUTPUT
    cs.value = True
    cs_pins.append(cs)

spi = busio.SPI(clock=board.GP6, MOSI=board.GP7)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

print("Writing displays...")

while True:
    for i, cs in enumerate(cs_pins):
        led.value = not led.value
        send(spi, make_group(f"Display {i}", COLORS[i]), cs)
        print(f"Display {i} done")

    print("All displays written")
