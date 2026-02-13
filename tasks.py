import os
from datetime import datetime

from invoke import task

DEFAULT_BOARD = "raspberry_pi_pico"


def get_mount_point() -> str:
    """Find the mounted CIRCUITPY volume."""
    for base in ("/media", "/run/media", "/Volumes"):
        if not os.path.isdir(base):
            continue
        for root, dirs, _ in os.walk(base):
            if "CIRCUITPY" in dirs:
                return os.path.join(root, "CIRCUITPY")
    raise FileNotFoundError("CIRCUITPY mount point not found")


@task
def deploy(c):
    """Sync src/ to the board root."""
    mount_point = get_mount_point()
    c.run(
        f"rsync -av --exclude '__pycache__' --exclude '*.pyc' --exclude '.gitkeep' src/ {mount_point}/"
    )
    c.run("sync")


@task
def repl(c):
    """Open an interactive REPL on the board."""
    c.run("mpremote connect auto repl", pty=True)


@task
def libs(c):
    """Install CircuitPython libraries onto the board via circup."""
    c.run("circup install -r circuitpython-requirements.txt")


@task
def reset(c):
    """Soft-reset the board."""
    c.run("mpremote connect auto reset")


@task
def set_rtc(c):
    """Set DS3231 RTC to the current host time."""
    now = datetime.now()
    struct_args = (
        f"{now.year}, {now.month}, {now.day}, "
        f"{now.hour}, {now.minute}, {now.second}, "
        f"{now.weekday()}, {now.timetuple().tm_yday}, -1"
    )
    code = (
        "import time, board, busio, adafruit_ds3231; "
        "i2c = busio.I2C(board.GP1, board.GP0); "
        f"rtc = adafruit_ds3231.DS3231(i2c); "
        f"rtc.datetime = time.struct_time(({struct_args})); "
        "t = rtc.datetime; "
        "print(f'{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}')"
    )
    c.run(f'mpremote exec "{code}"')


@task(optional=["board"])
def typecheck(c, board=DEFAULT_BOARD):
    """Run mypy against src/ using board-specific CircuitPython stubs."""
    c.run(f"circuitpython_setboard {board}")
    c.run("mypy src")
