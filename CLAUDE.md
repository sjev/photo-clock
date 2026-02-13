# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

CircuitPython photo clock for RP2040. A 4-digit clock where each digit is displayed as a separate image on individual displays. Uses a DS3231 RTC module over I2C for timekeeping.

## Commands

```bash
uv sync                          # install host dev dependencies
inv deploy                       # rsync src/ to mounted CIRCUITPY board
inv libs                         # install board libs via circup
inv repl                         # open board REPL via mpremote
inv reset                        # soft-reset board
inv set_rtc                      # sync DS3231 RTC to host time
inv typecheck                    # mypy with CircuitPython stubs (default: raspberry_pi_pico)
inv typecheck --board=<board_id> # mypy for a different board
ruff check --fix && ruff format  # lint and format
```

## Architecture

- **`src/`** — deployed 1:1 to the board root. `code.py` is the CircuitPython entry point.
- **`src/lib/`** — custom/vendored modules (git-tracked). Board libraries from circup are NOT here.
- **`tasks.py`** — invoke task definitions for deploy, REPL, libs, typecheck, RTC sync.
- **`scratch/`** — development/debugging utilities (not deployed).
- **`circuitpython-requirements.txt`** — board libraries installed via `circup`, not tracked in git.
- **`pyproject.toml`** — host dev tools only (ruff, mypy, mpremote, circup, invoke).

## Hardware

- **MCU:** RP2040 running CircuitPython >10.0
- **RTC:** DS3231 at I2C address `0x68` on GP0 (SDA) / GP1 (SCL)
- I2C init: `busio.I2C(board.GP1, board.GP0)`

## Code Conventions

- Target Python 3.11+ with type hints.
- CircuitPython board libraries use `# type: ignore` on import (not available on host).
- Ruff ignores F401, F821, E402 because CircuitPython libs aren't resolvable on host.
- Board libraries go in `circuitpython-requirements.txt`, not `pyproject.toml`.
- CircuitPython auto-reloads on file write — no manual reset after deploy.
