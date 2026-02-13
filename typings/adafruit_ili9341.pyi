class ILI9341:
    root_group: object | None

    def __init__(
        self,
        bus,
        *,
        width: int = ...,
        height: int = ...,
        rotation: int = ...,
    ) -> None: ...
