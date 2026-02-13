import displayio


class Label(displayio.Group):
    text: str
    color: int

    def __init__(
        self,
        font,
        *,
        text: str = ...,
        color: int = ...,
        scale: int = ...,
        x: int = ...,
        y: int = ...,
    ) -> None: ...
