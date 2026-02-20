import os
import random

import adafruit_ili9341  # type: ignore
import board  # type: ignore
import busio  # type: ignore
import digitalio  # type: ignore
import displayio  # type: ignore
import fourwire  # type: ignore
import sdcardio  # type: ignore
import storage  # type: ignore

SPI_BAUDRATE = 24_000_000
# GP4 is owned by FourWire; displays 1-3 have manual CS
EXTRA_CS_PINS = [board.GP21, board.GP22, board.GP26]


class DigitDisplay:
    """Wraps a single ILI9341 display addressed by manual CS toggling."""

    def __init__(self, display, cs) -> None:
        self._display = display
        self._cs = cs
        self._group = displayio.Group()
        self._current_digit: int | None = None

    def show_digit(self, digit: int) -> None:
        """Load a random image for digit and refresh this display."""
        if digit == self._current_digit:
            return
        self._current_digit = digit
        folder = f"/sd/{digit}"
        files = os.listdir(folder)
        path = f"{folder}/{random.choice(files)}"
        print(f"  loading {path}")
        bitmap = displayio.OnDiskBitmap(path)
        while len(self._group):
            self._group.pop()
        self._group.append(
            displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        )
        self._refresh()

    def force_refresh(self) -> None:
        """Re-send current content to the display."""
        if self._current_digit is not None:
            self._refresh()

    def _refresh(self) -> None:
        """Select this display, send framebuffer, deselect."""
        self._display.root_group = self._group
        if self._cs is not None:
            self._cs.value = False
        self._display.refresh()
        if self._cs is not None:
            self._cs.value = True
        print("  refreshed")


def main() -> None:
    """Main entry point."""
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    # SD card
    print("Mounting SD card...")
    sd_spi = busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=board.GP12)
    sd = sdcardio.SDCard(sd_spi, board.GP13)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")
    print("SD card mounted")

    # Extra CS pins — select for shared init alongside GP4
    extra_cs = []
    for i, pin in enumerate(EXTRA_CS_PINS):
        cs = digitalio.DigitalInOut(pin)
        cs.direction = digitalio.Direction.OUTPUT
        cs.value = False  # selected — will receive init alongside GP4
        extra_cs.append(cs)
        print(f"CS{i + 1} selected for init")

    # Display bus — GP4 as chip_select (FourWire manages it)
    displayio.release_displays()
    disp_spi = busio.SPI(clock=board.GP6, MOSI=board.GP7)
    bus = fourwire.FourWire(
        disp_spi, command=board.GP5, chip_select=board.GP4, baudrate=SPI_BAUDRATE,
    )
    print(f"FourWire bus created (baudrate={SPI_BAUDRATE})")

    # ILI9341 init — sent to ALL displays (GP4 by FourWire + extras held LOW)
    display = adafruit_ili9341.ILI9341(bus, width=320, height=240, auto_refresh=False)
    print("ILI9341 init sent to all displays")

    # Deselect extras after init
    for cs in extra_cs:
        cs.value = True
    print("Extra CS deselected")

    # Display 0 uses FourWire's native CS (GP4)
    # Displays 1-3 pull their CS LOW during refresh (GP4 also toggles, so display 0
    # gets stale data — we re-send display 0 last to fix it)
    displays = [DigitDisplay(display, None)]
    for cs in extra_cs:
        displays.append(DigitDisplay(display, cs))

    # Incrementing 4-digit counter
    counter = 0
    print("Starting counter loop")
    while True:
        led.value = not led.value
        digits = [
            counter // 1000 % 10,
            counter // 100 % 10,
            counter // 10 % 10,
            counter % 10,
        ]
        # Update displays 1-3 first, then display 0 last
        # (FourWire always toggles GP4, so display 0 sees all traffic)
        for disp, digit in zip(displays[1:], digits[1:]):
            disp.show_digit(digit)
        displays[0].show_digit(digits[0])
        # Re-send display 0 if any other display was updated
        displays[0].force_refresh()

        if counter % 100 == 0:
            print(f"counter={counter:04d}")
        counter = (counter + 1) % 10000


main()
