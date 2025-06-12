import pytest

from smartutils.error import base


class TestBaseError:
    def test_base_error_init_and_dict(self):
        err = base.BaseError(
            detail="foobar error", code=1234, msg="oops", status_code=400
        )
        dct = err.as_dict
        assert dct["code"] == 1234
        assert dct["msg"] == "oops"
        assert dct["status_code"] == 400
        assert dct["data"] is None
        # debug=False时，detail字段应为空
        assert dct["detail"] == ""

    def test_base_error_detail_debug(self):
        base.BaseData.set_debug(True)
        err = base.BaseError(detail="trace info", code=2, msg="aa", status_code=500)
        dct = err.as_dict
        assert dct["detail"] == "trace info"
        base.BaseData.set_debug(False)  # 恢复默认

    def test_base_error_is_ok_and_ok_obj(self):
        ok = base.OK
        assert ok.code == 0
        assert ok.status_code == 200
        assert ok.is_ok
        # OK对象dict
        dct = ok.as_dict
        assert dct["code"] == 0
        assert dct["status_code"] == 200
        assert dct["msg"] == "success"
        # OK.detail为空
        assert dct["detail"] == ""

    def test_basedatadict_properties(self):
        err = base.BaseError(detail="", code=101, msg="xmsg", status_code=601)
        dct = err.as_dict
        # BaseDataDict.status_code
        assert dct.status_code == 601
        # BaseDataDict.data
        # 除status_code外键值
        data_part = dct.data
        assert "status_code" not in data_part.keys()
        assert data_part["code"] == 101
        assert data_part["msg"] == "xmsg"
        assert data_part["detail"] == ""
        assert data_part["data"] is None
