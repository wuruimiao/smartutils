import pytest

import smartutils.app.auth.password as pwmod


@pytest.mark.skipif(pwmod.bcrypt is None, reason="bcrypt not installed")
def test_hash_and_check_password():
    helper = pwmod.PasswordHelper()
    plain = "abc$12345!"
    salt, hashed = helper.hash_password(plain)
    assert isinstance(salt, str) and salt
    assert isinstance(hashed, str) and hashed
    # 检查同样密码能验证通过
    assert helper.check_password(plain, hashed)
    # 错误密码应返回False
    assert helper.check_password("wrongpassword", hashed) is False


def test_check_password_invalid(mocker):
    """测试bcrypt.checkpw抛出异常时，应该抛出异常或False（边界）"""
    helper = pwmod.PasswordHelper()

    class DummyBcrypt:
        def checkpw(self, *a, **kw):
            raise ValueError("synthetic")

    mocker.patch.object(pwmod, "bcrypt", DummyBcrypt())
    with pytest.raises(ValueError):
        helper.check_password("x", "y")


def test_hash_password_invalid(mocker):
    """测试bcrypt.hashpw异常"""
    helper = pwmod.PasswordHelper()

    class DummyBcrypt:
        def gensalt(self):
            return b"0salt"

        def hashpw(self, *a, **kw):
            raise RuntimeError("bad hash")

    mocker.patch.object(pwmod, "bcrypt", DummyBcrypt())
    with pytest.raises(RuntimeError):
        helper.hash_password("p")
