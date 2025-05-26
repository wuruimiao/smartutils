import base64
from io import BytesIO
from typing import Tuple

from smartutils.log import logger

try:
    import pyotp
    import qrcode
except ImportError:
    logger.debug("smartutils.infra.auth.otp.OtpHelper depend on pyotp & qrcode, install before use.")
    pyotp, qrcode = None, None

from smartutils.config import ConfKey
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory

__all__ = ["OtpHelper"]


@singleton
class OtpHelper:
    @staticmethod
    def generate_qr(username: str) -> Tuple[str, str]:
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
        totp = pyotp.TOTP(otp_secret)
        return totp.verify(user_totp)


@InfraFactory.register(ConfKey.OTP, need_conf=False)
def _(conf):
    return OtpHelper()
