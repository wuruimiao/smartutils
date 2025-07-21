from types import SimpleNamespace
from unittest.mock import patch

import pytest

import smartutils.app.auth.token as token_mod


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


def test_generate_and_verify_token_and_refresh_token(user):
    conf = make_conf()
    # 使用一个很大的时间戳
    fake_now = 9999999999999999
    expected_access_exp = fake_now + conf.access_exp_min * 60
    expected_refresh_exp = fake_now + conf.refresh_exp_day * 24 * 60 * 60
    with patch("smartutils.time.get_now_stamp_float", return_value=fake_now):
        helper = token_mod.TokenHelper(conf)
        access, refresh = helper.token(user)

        assert access.exp == expected_access_exp
        assert refresh.exp == expected_refresh_exp

        # 检查 token payload
        decoded_access = token_mod.jwt.decode(
            access.token, conf.access_secret, algorithms=["HS256"]
        )
        assert decoded_access["userid"] == user.id
        assert decoded_access["username"] == user.name
        assert decoded_access["exp"] == expected_access_exp

        decoded_refresh = token_mod.jwt.decode(
            refresh.token, conf.refresh_secret, algorithms=["HS256"]
        )
        assert decoded_refresh["userid"] == user.id
        assert decoded_refresh["username"] == user.name
        assert decoded_refresh["exp"] == expected_refresh_exp

        decoded_access = token_mod.TokenHelper.verify_token(
            access.token, conf.access_secret
        )
        assert decoded_access
        assert decoded_access["userid"] == user.id
        assert decoded_access["username"] == user.name
        assert decoded_access["exp"] == expected_access_exp

        decoded_refresh = token_mod.TokenHelper.verify_token(
            refresh.token, conf.refresh_secret
        )
        assert decoded_refresh
        assert decoded_refresh["userid"] == user.id
        assert decoded_refresh["username"] == user.name
        assert decoded_refresh["exp"] == expected_refresh_exp

        helper = token_mod.TokenHelper(conf)
        result = helper.refresh(refresh.token)
        assert result
        access, refresh = result
        decoded_access = token_mod.TokenHelper.verify_token(
            access.token, conf.access_secret
        )
        assert decoded_access
        assert decoded_access["userid"] == user.id
        assert decoded_access["username"] == user.name
        assert decoded_access["exp"] == expected_access_exp

        decoded_refresh = token_mod.TokenHelper.verify_token(
            refresh.token, conf.refresh_secret
        )
        assert decoded_refresh
        assert decoded_refresh["userid"] == user.id
        assert decoded_refresh["username"] == user.name


def test_tokenhelper_missing_jwt(monkeypatch):
    monkeypatch.setattr(token_mod, "jwt", None)
    with pytest.raises(AssertionError):
        token_mod.TokenHelper(conf=None)  # conf内容可以mock，主要测assert分支


def test_tokenhelper_expired():
    conf = make_conf()
    from smartutils.time import get_now_stamp_float

    fake_expired_now = get_now_stamp_float() - 3600
    user = token_mod.User(id=123, name="test2")
    with patch("smartutils.time.get_now_stamp_float", return_value=fake_expired_now):
        helper = token_mod.TokenHelper(conf)
        access, _ = helper.token(user)
    # 此时token.exp < 当前now
    result = token_mod.TokenHelper.verify_token(access.token, conf.access_secret)
    assert result is None


def test_tokenhelper_verify_token_invalid():
    conf = make_conf()
    # 此时token.exp < 当前now
    result = token_mod.TokenHelper.verify_token("invalid_token", conf.access_secret)
    assert result is None


def test_tokenhelper_refresh_invalid():
    conf = make_conf()
    # 此时token.exp < 当前now
    result = token_mod.TokenHelper(conf).refresh("invalid_token")
    assert result is None


def test_tokenhelper_verify_access_token(user):
    conf = make_conf()
    helper = token_mod.TokenHelper(conf)
    access_token, _ = helper.token(user)
    # 正常token
    payload = helper.verify_access_token(access_token.token)
    assert payload
    assert payload.id == user.id
    assert payload.name == user.name

    # 异常token
    invalid = helper.verify_access_token("invalid_token_for_access")
    assert invalid is None
