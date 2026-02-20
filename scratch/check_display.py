"""Check all 4 ILI9341 displays — shows 'Display N' on each."""

import board
import busio
import displayio
import fourwire
import terminalio

import adafruit_ili9341
from adafruit_display_text import label

CS_PINS = [board.GP4, board.GP21, board.GP22, board.GP26]
COLORS = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00]

displayio.release_displays()
spi = busio.SPI(clock=board.GP6, MOSI=board.GP7)

displays = []
for pin in CS_PINS:
    bus = fourwire.FourWire(spi, command=board.GP5, chip_select=pin, baudrate=24_000_000)
    display = adafruit_ili9341.ILI9341(bus, width=320, height=240, auto_refresh=False)
    displays.append(display)

print("Init done, writing to displays...")


def make_group(text: str, color: int) -> displayio.Group:
    """Create a group with colored background and centered text."""
    group = displayio.Group()
    bg = displayio.Bitmap(320, 240, 1)
    palette = displayio.Palette(1)
    palette[0] = color
    group.append(displayio.TileGrid(bg, pixel_shader=palette))
    group.append(label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=100, y=120, scale=3))
    return group


for i, disp in enumerate(displays):
    print(f"Writing Display {i}")
    disp.root_group = make_group(f"Display {i}", COLORS[i])
    disp.refresh()

print("All displays written")
