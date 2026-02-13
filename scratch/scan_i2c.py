"""Scan I2C bus for connected devices."""

import board
import busio

i2c = busio.I2C(board.GP1, board.GP0)

while not i2c.try_lock():
    pass

try:
    devices = i2c.scan()
    if devices:
        print("Found I2C devices at:", [hex(d) for d in devices])
    else:
        print("No I2C devices found — check wiring")
finally:
    i2c.unlock()
