from unittest.mock import MagicMock, patch

import pytest

import smartutils.infra.auth.otp as otpmodule


@pytest.mark.skipif(
    otpmodule.pyotp is None or otpmodule.qrcode is None,
    reason="pyotp or qrcode not installed",
)
def test_generate_qr_and_verify_totp():
    helper = otpmodule.OtpHelper()
    username = "userA"
    secret, qr_img = helper.generate_qr(username)
    assert isinstance(secret, str) and len(secret) >= 16
    assert isinstance(qr_img, str) and len(qr_img) > 100  # base64 string length
    # 使用刚生成secret生成TOTP码
    totper = otpmodule.pyotp.TOTP(secret)
    code = totper.now()
    assert helper.verify_totp(secret, code) is True
    assert helper.verify_totp(secret, "000000") is False


def test_qr_b64_pic(monkeypatch):
    # 强控二维码生成内容，更易断言
    monkeypatch.setattr(otpmodule, "pyotp", MagicMock())
    monkeypatch.setattr(otpmodule, "qrcode", MagicMock())
    fake_img_bytes = b"testimgdata"

    class DummyImg:
        def save(self, buf, format=None):
            buf.write(fake_img_bytes)

    otpmodule.pyotp.random_base32 = MagicMock(return_value="SECRET12")
    totp = MagicMock()
    totp.provisioning_uri.return_value = "otpauth://auth"
    otpmodule.pyotp.TOTP = MagicMock(return_value=totp)
    otpmodule.qrcode.make = MagicMock(return_value=DummyImg())
    # 断言base64流程
    secret, img_b64 = otpmodule.OtpHelper.generate_qr("userB")
    assert secret == "SECRET12"
    import base64

    assert img_b64 == base64.b64encode(fake_img_bytes).decode("utf-8")


def test_verify_totp_mock(monkeypatch):
    # TOTP返回True/False流程
    monkeypatch.setattr(otpmodule, "pyotp", MagicMock())
    totp = MagicMock()
    totp.verify.return_value = True
    otpmodule.pyotp.TOTP = MagicMock(return_value=totp)
    assert otpmodule.OtpHelper.verify_totp("sec", "111222") is True
    totp.verify.return_value = False
    assert otpmodule.OtpHelper.verify_totp("sec", "333333") is False
