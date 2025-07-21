from smartutils.error.sys import LibraryUsageError


class LibraryCheckMixin:
    required_libs = {}
    require_conf = True  # 默认检查conf

    def check(self, conf=None):
        not_loaded = [name for name, lib in self.required_libs.items() if not lib]
        if not_loaded:
            libs_str = ", ".join(not_loaded)
            raise LibraryUsageError(
                f"{self.__class__.__name__} depend on {libs_str}, install first!"
            )

        if self.require_conf:
            if conf is None:
                raise LibraryUsageError(
                    f"{self.__class__.__name__} must init by infra."
                )
