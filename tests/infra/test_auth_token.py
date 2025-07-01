import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import jwt
import pytest

import smartutils.infra.auth.token as token_mod


def make_conf():
    return SimpleNamespace(
        access_secret="secret1",
        access_exp_min=1,  # 分钟
        refresh_secret="secret2",
        refresh_exp_day=1,  # 天
    )


@pytest.fixture
def user():
    return token_mod.User(id=123, name="test")


@patch("smartutils.infra.auth.token.jwt")
@patch("smartutils.infra.auth.token.get_stamp_after")
def test_generate_and_verify_token(mock_stamp, mock_jwt, user):
    mock_stamp.return_value = 1234567
    mock_jwt.encode.return_value = "jwt-token"
    mock_jwt.decode.return_value = {
        "userid": user.id,
        "username": user.name,
        "exp": 1234567,
    }
    conf = make_conf()
    helper = token_mod.TokenHelper(conf)
    # 生成token
    access, refresh = helper.token(user)
    assert access.token == "jwt-token" and refresh.token == "jwt-token"
    assert access.exp == 1234567 and refresh.exp == 1234567
    # 校验token
    payload = helper.verify_token("jwt-token", conf.access_secret)
    assert payload
    assert payload["userid"] == 123 and payload["exp"] == 1234567


def test_verify_token_exceptions():
    with patch("smartutils.infra.auth.token.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError("expired")
        assert (
            token_mod.TokenHelper.verify_token("abc", "secret") is None
        )  # 期望因过期返回 None
        mock_decode.side_effect = jwt.InvalidTokenError("bad")
    assert token_mod.TokenHelper.verify_token("abc", "secret") is None


def test_tokenhelper_missing_jwt(monkeypatch):
    monkeypatch.setattr(token_mod, "jwt", None)
    with pytest.raises(AssertionError):
        token_mod.TokenHelper(conf=None)  # conf内容可以mock，主要测assert分支


def test_tokenhelper_expired(monkeypatch):
    class MockJWT:
        class ExpiredSignatureError(Exception):
            pass

        class InvalidTokenError(Exception):
            pass

        @staticmethod
        def decode(*a, **k):
            raise MockJWT.ExpiredSignatureError()

    monkeypatch.setattr(token_mod, "jwt", MockJWT)
    # 直接调用静态方法，无需实例化
    assert token_mod.TokenHelper.verify_token("dummy", "secret") is None
