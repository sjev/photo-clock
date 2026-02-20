# System design


This project is about creating a 4-digit clock.
Each digit is a separate display displaying images.

## Hardware

* uC — RP2040 running CircuitPython >10.0
* RTC — DS3231
* Display — 2.2" TFT ILI9341 (240×320, SPI) with onboard SD card slot
* SD card — on display module, connected via SPI1

Source: [tinytronics](https://www.tinytronics.nl/en/displays/tft/2.2-inch-tft-display-240*320-pixels-ili9341)

## Wiring

[PINOUT](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico-1-family)

![rpi_non_wireless](https://www.raspberrypi.com/documentation/microcontrollers/images/pico-pinout.svg)


| RP2040 Pin | Bus | Device Pin | Function |
|------------|-----|------------|----------|
| GP0 (pin 1) | I2C0 SDA | DS3231 SDA | I2C data |
| GP1 (pin 2) | I2C0 SCL | DS3231 SCL | I2C clock |
| GP4 (pin 6) | — | Display 0 CS | Chip select (digit 0) |
| GP5 (pin 7) | — | Display DC | Data/Command select (shared) |
| GP6 (pin 9) | SPI0 SCK | Display SCK | SPI clock (shared) |
| GP7 (pin 10) | SPI0 TX | Display MOSI | SPI data out (shared) |
| GP21 (pin 27) | — | Display 1 CS | Chip select (digit 1) |
| GP22 (pin 29) | — | Display 2 CS | Chip select (digit 2) |
| GP26 (pin 31) | — | Display 3 CS | Chip select (digit 3) |
| GP10 (pin 14) | SPI1 SCK | SD_SCK | SD card clock |
| GP11 (pin 15) | SPI1 TX | SD_MOSI | SD card data out |
| GP12 (pin 16) | SPI1 RX | SD_MISO | SD card data in |
| GP13 (pin 17) | — | SD_CS | SD card chip select |
| 3V3 (pin 36) | — | VCC, RST, LED | Power + hardwired lines |
| GND (pin 38) | — | GND | Ground |

All display F_CS and MISO left unconnected.

### Notes

* **I2C:** DS3231 at address `0x68`. Module has onboard 4.7kΩ pull-ups. SQW/32K unused.
* **SPI0 (displays):** `busio.SPI(clock=board.GP6, MOSI=board.GP7)` — write-only, no MISO. Shared by all 4 displays. MOSI↔SCK crossover unavoidable (SPI0 SCK is always on a lower GPIO than TX).
* **SPI1 (SD card):** `busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=board.GP12)`
* **Display CS pins:** GP4 (digit 0), GP21 (digit 1), GP22 (digit 2), GP26 (digit 3). DC (GP5) shared by all displays.
* **RST / LED:** Tied to 3V3 (no software reset, backlight always on).
* **Board libraries:** `adafruit_ds3231`, `adafruit_ili9341`.

### 4-display setup

4 displays share SPI0 bus (SCK, MOSI) and DC line. Each display has a unique CS pin. Only one display is addressed at a time by pulling its CS low.

## Wiring diagram

![Wiring diagram](img/wiring.png)

Generated with [WireViz](https://github.com/wireviz/WireViz) from [`wiring.yml`](wiring.yml). Regenerate with `inv wiring`.
