import time

import adafruit_ds3231
import adafruit_ili9341
import board
import busio
import digitalio
import displayio
import fourwire
import rainbowio
import terminalio
from adafruit_display_text import label


def main() -> None:
    """Main entry point."""
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    # RTC
    i2c = busio.I2C(board.GP1, board.GP0)
    rtc = adafruit_ds3231.DS3231(i2c)

    # Display
    displayio.release_displays()
    spi = busio.SPI(clock=board.GP6, MOSI=board.GP7)
    display_bus = fourwire.FourWire(spi, command=board.GP5, chip_select=board.GP4)
    display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

    group = displayio.Group()
    bitmap = displayio.Bitmap(320, 240, 1)
    palette = displayio.Palette(1)
    palette[0] = 0x000000
    group.append(displayio.TileGrid(bitmap, pixel_shader=palette))

    time_label = label.Label(
        terminalio.FONT, text="00:00:00", color=0xFFFFFF, scale=4, x=80, y=120
    )
    group.append(time_label)
    display.root_group = group

    color_pos = 0
    while True:
        led.value = not led.value
        t = rtc.datetime
        time_str = f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"
        time_label.text = time_str
        time_label.color = rainbowio.colorwheel(color_pos)
        color_pos = (color_pos + 32) % 256
        print(time_str)
        time.sleep(1.0)


main()
