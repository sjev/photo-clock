# System design


This project is about creating a 4-digit clock.
Each digit is a separate display displaying images.

## Hardware

* uC - RP2040 running Circuitpython >10.0
* RTC DS3231
* Display: 4x 2.2" TFT ILI9341 (240×320, SPI)


## RTC functionality

### Connections

[PINOUT](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico-1-family)


| DS3231 Pin | RP2040 Pin | Function |
|------------|------------|----------|
| VCC | 3V3 (pin 36) | Power (3.3V) |
| GND | GND (pin 38) | Ground |
| SDA | GP0 (pin 1) | I2C data |
| SCL | GP1 (pin 2) | I2C clock |

SQW and 32K pins are unused. SQW could later drive an alarm interrupt if needed.

* DS3231 module has onboard pull-ups (4.7kΩ) for SDA/SCL — no external resistors needed.
* GP0/GP1 are the default `I2C0` bus on the Pico. In CircuitPython: `busio.I2C(board.GP1, board.GP0)`.
* DS3231 I2C address is `0x68`.
* Board library: `adafruit_ds3231`.


## Display

4x ILI9341 2.2" TFT (240×320) connected via a shared SPI bus with individual chip-select lines.

### Single display (minimum wiring)

4 GPIO pins. RST and BLK hardwired. One MOSI↔SCK crossover — unavoidable since SPI0 always has SCK on a lower GPIO than TX.

| Display Pin | RP2040 Pin | Notes |
|-------------|-----------|-------|
| VCC | 3V3 (pin 36) | Power |
| GND | GND (pin 38) | Ground |
| CS | GP4 (pin 6) | Chip select |
| RST | tie to 3V3 | No software reset needed |
| DC | GP5 (pin 7) | Data/Command select |
| MOSI | GP7 (pin 10) | SPI0 TX — swaps with SCK |
| SCK | GP6 (pin 9) | SPI0 SCK — swaps with MOSI |
| LED | tie to 3V3 | Backlight always on |
| MISO | unconnected | Write-only operation |

In CircuitPython: `busio.SPI(clock=board.GP6, MOSI=board.GP7)`.

### Full setup (4 displays)

All displays share a single SPI0 bus plus DC, RST, and backlight lines. Only the CS pin is unique per display — the CS-selected display is the only one that listens to the bus, so sharing DC is safe.

| Signal | RP2040 Pin | Shared? | Notes |
|--------|-----------|---------|-------|
| SPI SCK | GP6 (pin 9) | all displays | SPI0 SCK |
| SPI MOSI | GP7 (pin 10) | all displays | SPI0 TX |
| DC | GP5 (pin 7) | all displays | Data/Command select |
| RST | GP8 (pin 11) | all displays | Reset all on startup |
| BLK | GP9 (pin 12) | all displays | Backlight (tie high or PWM) |
| CS 0 | GP4 (pin 6) | — | Display 0 (ones minute) |
| CS 1 | GP10 (pin 14) | — | Display 1 (tens minute) |
| CS 2 | GP11 (pin 15) | — | Display 2 (ones hour) |
| CS 3 | GP12 (pin 16) | — | Display 3 (tens hour) |

* MISO pin on each display module left unconnected.

* Board library: `adafruit_ili9341`.

## Wiring diagram

![Wiring diagram](img/wiring.png)

Generated with [WireViz](https://github.com/wireviz/WireViz) from [`wiring.yml`](wiring.yml). Regenerate with `inv wiring`.
