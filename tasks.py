from invoke import task

DEFAULT_BOARD = "raspberry_pi_pico"


@task
def deploy(c):
    """Sync src/ to the board root."""
    c.run("mpremote connect auto cp -r src/. :/")


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


@task(optional=["board"])
def typecheck(c, board=DEFAULT_BOARD):
    """Run mypy against src/ using board-specific CircuitPython stubs."""
    c.run(f"circuitpython_setboard {board}")
    c.run("mypy src")
