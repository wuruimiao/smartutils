import base64
from io import BytesIO
from typing import Tuple

try:
    import pyotp
    import qrcode
except ImportError:
    pyotp = None
    qrcode = None

from smartutils.config import ConfKey
from smartutils.design import singleton
from smartutils.error.sys import LibraryUsageError
from smartutils.infra.factory import InfraFactory

__all__ = ["OtpHelper"]


def _check_dep():
    if not pyotp or qrcode:
        raise LibraryUsageError("use otp must install pyotp and qrcode, by install [auth]")


@singleton
class OtpHelper:
    @staticmethod
    def generate_qr(username: str) -> Tuple[str, str]:
        _check_dep()
        otp_secret = pyotp.random_base32()
        totp = pyotp.TOTP(otp_secret)

        otp_auth_url = totp.provisioning_uri(name=username, issuer_name="auth")

        img = qrcode.make(otp_auth_url)
        buf = BytesIO()
        img.save(buf, format="PNG")
        img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        return otp_secret, img_str

    @staticmethod
    def verify_totp(otp_secret: str, user_totp: str) -> bool:
        _check_dep()
        totp = pyotp.TOTP(otp_secret)
        return totp.verify(user_totp)


@InfraFactory.register(ConfKey.OTP, need_conf=False)
def _(conf):
    return OtpHelper()
