import time

class DS3231:
    datetime: time.struct_time

    def __init__(self, i2c) -> None: ...
