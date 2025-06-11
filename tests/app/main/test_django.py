import sys
import types
import pytest
from unittest import mock

def gen_mock_settings():
    settings = types.SimpleNamespace()
    settings.MIDDLEWARE = []
    settings.ROOT_URLCONF = ''
    return settings

@mock.patch("smartutils.app.main.django.settings", new_callable=gen_mock_settings)
@mock.patch("smartutils.app.main.django.MiddlewareFactory")
@mock.patch("smartutils.app.main.django.ExceptionPlugin")
@mock.patch("smartutils.app.main.django.HeaderPlugin")
@mock.patch("smartutils.app.main.django.LogPlugin")
@mock.patch("smartutils.app.main.django.get_wsgi_application", return_value="app_obj")
@mock.patch("smartutils.app.main.django._init_smartutils")
def test_create_app_sets_middleware_and_urls(mock_init, mock_wsgi, mock_log, mock_header, mock_except, mock_mw_factory, mock_settings):
    # arrange
    from smartutils.app.main.django import create_app
    
    # Middlewares as basic lambda
    mock_mw_factory.get.return_value.return_value.return_value = lambda x: x
    mock_except.return_value = mock.Mock()
    mock_header.return_value = mock.Mock()
    mock_log.return_value = mock.Mock()
    # act
    app = create_app("dummy.yaml")
    # assert
    assert app == "app_obj"
    assert mock_settings.MIDDLEWARE
    assert any(call in str(mock_settings.MIDDLEWARE) for call in ['ExceptionPlugin','HeaderPlugin','LogPlugin']) or len(mock_settings.MIDDLEWARE)==3
    assert mock_settings.ROOT_URLCONF == "smartutils_auto_urls"
    assert "smartutils_auto_urls" in sys.modules
    # check route view
    urls = sys.modules["smartutils_auto_urls"]
    assert hasattr(urls, "urlpatterns")
    match_names = [r.callback.__name__ for r in urls.urlpatterns]
    assert "root_view" in match_names and "healthy_view" in match_names

@mock.patch("smartutils.app.main.django.settings", new_callable=gen_mock_settings)
@mock.patch("smartutils.app.main.django.MiddlewareFactory")
@mock.patch("smartutils.app.main.django.ExceptionPlugin")
@mock.patch("smartutils.app.main.django.HeaderPlugin")
@mock.patch("smartutils.app.main.django.LogPlugin")
@mock.patch("smartutils.app.main.django.get_wsgi_application", return_value="app_obj")
@mock.patch("smartutils.app.main.django._init_smartutils")
def test_create_app_when_urls_exist(mock_init, mock_wsgi, mock_log, mock_header, mock_except, mock_mw_factory, mock_settings):
    from smartutils.app.main.django import create_app
    # ROOT_URLCONF 已存在
    mock_settings.ROOT_URLCONF = "exists.urls"
    mock_mw_factory.get.return_value.return_value.return_value = lambda x: x
    mock_except.return_value = mock.Mock()
    mock_header.return_value = mock.Mock()
    mock_log.return_value = mock.Mock()
    app = create_app()
    assert app == "app_obj"
    assert mock_settings.ROOT_URLCONF == "exists.urls"

@mock.patch("smartutils.app.main.django.settings", new_callable=gen_mock_settings)
def test_create_app_no_middleware(mock_settings):
    # 模拟没有 MIDDLEWARE 属性
    delattr(mock_settings, "MIDDLEWARE")
    import smartutils.app.main.django as django_mod
    django_mod.settings = mock_settings
    django_mod._init_smartutils = lambda x: None
    django_mod.MiddlewareFactory = mock.Mock()
    django_mod.ExceptionPlugin = mock.Mock()
    django_mod.HeaderPlugin = mock.Mock()
    django_mod.LogPlugin = mock.Mock()
    django_mod.get_wsgi_application = lambda: "app_obj"
    app = django_mod.create_app()
    assert hasattr(mock_settings, "MIDDLEWARE")
    assert app == "app_obj"
