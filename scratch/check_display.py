"""Check ILI9341 display — fills screen red, then shows text."""

import board
import busio
import displayio
import fourwire  # type: ignore
import terminalio

import adafruit_ili9341  # type: ignore
from adafruit_display_text import label  # type: ignore

displayio.release_displays()

spi = busio.SPI(clock=board.GP6, MOSI=board.GP7)
display_bus = fourwire.FourWire(spi, command=board.GP5, chip_select=board.GP4)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

group = displayio.Group()

# Red background
bitmap = displayio.Bitmap(320, 240, 1)
palette = displayio.Palette(1)
palette[0] = 0xFF0000
group.append(displayio.TileGrid(bitmap, pixel_shader=palette))

# White text
text = label.Label(terminalio.FONT, text="Hello Clock!", color=0xFFFFFF, x=80, y=120)
group.append(text)

display.root_group = group

print("Display check OK — red screen with white text")
