"""Check SD card on SPI1 — mounts card and lists contents."""

import os

import board
import busio
import sdcardio
import storage

spi = busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=board.GP12)
sd = sdcardio.SDCard(spi, board.GP13)
vfs = storage.VfsFat(sd)
storage.mount(vfs, "/sd")

print("SD card mounted at /sd")
print(f"Size: {sd.count() * 512 / 1024 / 1024:.0f} MB")
print()

for entry in sorted(os.listdir("/sd")):
    stat = os.stat(f"/sd/{entry}")
    is_dir = stat[0] & 0x4000
    if is_dir:
        print(f"  {entry}/")
    else:
        size_kb = stat[6] / 1024
        print(f"  {entry}  ({size_kb:.1f} KB)")
