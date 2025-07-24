class MyBase:
    @property
    def name(self):
        return f"[{self.__class__.__name__}]"

    @property
    def full_name(self):
        return f"[{self.__class__.__module__}.{self.__class__.__qualname__}]"
