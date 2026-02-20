import displayio

class ILI9341:
    root_group: displayio.Group | None

    def __init__(
        self,
        bus,
        *,
        width: int = ...,
        height: int = ...,
        rotation: int = ...,
        auto_refresh: bool = ...,
    ) -> None: ...
    def refresh(self) -> None: ...
