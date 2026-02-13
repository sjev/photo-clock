class FourWire:
    def __init__(
        self,
        spi,
        *,
        command,
        chip_select,
        reset=None,
        baudrate: int = ...,
        polarity: int = ...,
        phase: int = ...,
    ) -> None: ...
