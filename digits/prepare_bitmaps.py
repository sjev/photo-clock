#!/usr/bin/env python3
"""Fetch cat images with digit overlays from cataas.com and convert to BMP.

Produces 10 images per digit (0–9) sized for the ILI9341 display (240×320).
Output: digits/sd/{digit}/00.bmp .. 09.bmp

Copyright (c) 2026 - Jev Kuznetsov
"""

import io
import time
from pathlib import Path

import requests
from PIL import Image

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
FONT_SIZE = 150
IMAGES_PER_DIGIT = 10
BASE_URL = "https://cataas.com/cat/says"
OUTPUT_DIR = Path(__file__).parent / "sd"


def fetch_cat_image(digit: int) -> bytes:
    """Fetch a cat image with digit overlay from cataas.com."""
    url = f"{BASE_URL}/{digit}"
    params = {
        "fontSize": FONT_SIZE,
        "width": DISPLAY_WIDTH,
        "height": DISPLAY_HEIGHT,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.content


def convert_to_bmp(data: bytes) -> Image.Image:
    """Convert raw image bytes to a landscape BMP for the ILI9341 display."""
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")
    if img.size != (DISPLAY_WIDTH, DISPLAY_HEIGHT):
        img = img.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    img = img.rotate(-90, expand=True)
    return img


def main() -> None:
    for digit in range(10):
        digit_dir = OUTPUT_DIR / str(digit)
        digit_dir.mkdir(parents=True, exist_ok=True)

        for idx in range(IMAGES_PER_DIGIT):
            path = digit_dir / f"{idx:02d}.bmp"
            print(f"Fetching digit {digit} image {idx:02d}...", end=" ", flush=True)

            try:
                data = fetch_cat_image(digit)
                img = convert_to_bmp(data)
                img.save(path, "BMP")
                print(f"saved {path}")
            except requests.RequestException as e:
                print(f"FAILED: {e}")
                continue

            time.sleep(0.5)  # be polite to the API


if __name__ == "__main__":
    main()
