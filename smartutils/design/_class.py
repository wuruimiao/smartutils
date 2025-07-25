class classproperty(property):
    def __get__(self, obj, cls):
        return self.fget(cls)


class MyBase:
    @classproperty
    def name(cls):
        return f"[{cls.__name__}]"

    @classproperty
    def full_name(cls):
        # 限定名，含作用域
        return f"[{cls.__module__}.{cls.__qualname__}]"
