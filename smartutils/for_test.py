from typing import Optional


class ForTest:
    def __init__(self, mocker) -> None:
        self._msgs = []
        self._mocker = mocker
        self._patch_log()

    def patch(self, module, name: str, v, ret_value: bool = False):
        if ret_value:
            self._mocker.patch.object(module, name, return_value=v)
        else:
            self._mocker.patch.object(module, name, v)

    def _patch_log(self):
        from smartutils import log

        for level in ("info", "error", "debug", "warning"):
            ori = getattr(log.logger, level)

            def _fake(msg, *args, _level=level, **kwargs):
                self._msgs.append((_level, msg, args))
                return ori(msg, *args, **kwargs)

            self.patch(log.logger, level, _fake)

    def assert_log(self, msg: str, *args, level: Optional[str] = None, **kwargs):
        found = False
        for item in self._msgs:
            found = (
                msg == item[1]
                and args == item[2]
                and (level is None or level == item[0])
            )
            if found:
                return
        assert False, f"日志：{self._msgs}"
