# photo-clock

CircuitPython project for RP2040.

## Tooling

| Tool | Purpose |
|------|---------|
| `uv` | Host environment and dev dependency management |
| `ruff` | Linting and formatting |
| `mpremote` | File sync and REPL access |
| `circup` | Board library installation |
| `invoke` | Task runner |

## Setup

```bash
uv sync
```

## Workflow

```bash
inv deploy   # sync src/ to board  (mpremote cp)
inv libs     # install board libs  (circup)
inv repl     # open board REPL
inv reset    # soft-reset board
inv typecheck  # run mypy with board-specific stubs
```

CircuitPython auto-reloads when files are written — no manual reset needed after `deploy`.

`inv typecheck` defaults to `raspberry_pi_pico`. Override with `inv typecheck --board=<board_id>`
if you are targeting a different board.

## Structure

```
src/         # deployed 1:1 to board root
  code.py    # entry point
  lib/       # custom/vendored modules (git-tracked)
circuitpython-requirements.txt  # board libs managed by circup
pyproject.toml                  # host dev tools only
```

## Adding board libraries

Add the library name to `circuitpython-requirements.txt`, then run `inv libs`.
These are installed directly onto the board and are **not** tracked in git.
