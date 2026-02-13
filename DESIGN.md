# System design


This project is about creating a 4-digit clock.
Each digit is a separate display displaying images.

## Hardware

* uC - RP2040 running Circuitpython >10.0
* RTC DS3231


## RTC functionality

### Connections

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
