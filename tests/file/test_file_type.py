import sys
import types

import pytest

from smartutils.file import _type


class DummyKind:
    def __init__(self, mime, ext):
        self.mime = mime
        self.extension = ext


@pytest.fixture(autouse=True)
def patch_filetype(mocker):
    dummy = types.SimpleNamespace()
    dummy.guess = lambda filepath: None  # 默认无识别

    mocker.patch.dict(sys.modules, {"filetype": dummy})
    mocker.patch.object(_type, "filetype", dummy)
    yield


def test_file_mime_none():
    assert _type.file_mime("xx.any") == ""


def test_file_type_none():
    assert _type.file_type("abc.zzz") == ""


def test_first_type_none():
    assert _type._first_type("notfound.xxx") == ""


def test_file_mime_image(mocker):
    mocker.patch.object(
        _type.filetype, "guess", lambda fp: DummyKind("image/png", "png")
    )
    assert _type.file_mime("pic.png") == "image/png"
    assert _type._first_type("pic.png") == "image"
    assert _type.is_img("pic.png") is True
    assert _type.is_video("pic.png") is False
    assert _type.is_audio("pic.png") is False


def test_file_type_video(mocker):
    mocker.patch.object(
        _type.filetype, "guess", lambda fp: DummyKind("video/mp4", "mp4")
    )
    assert _type.file_type("video.mp4") == "mp4"
    assert _type._first_type("video.mp4") == "video"
    assert _type.is_img("video.mp4") is False
    assert _type.is_video("video.mp4") is True


def test_is_archive(mocker):
    # 命中压缩类型
    mocker.patch.object(
        _type.filetype, "guess", lambda fp: DummyKind("application/zip", "zip")
    )
    assert _type.is_archive("test.zip") is True
    # 不支持类型
    mocker.patch.object(
        _type.filetype, "guess", lambda fp: DummyKind("text/plain", "txt")
    )
    assert _type.is_archive("test.txt") is False


def test_is_doc_always_false(mocker):
    mocker.patch.object(
        _type.filetype, "guess", lambda fp: DummyKind("application/msword", "docx")
    )
    assert _type.is_doc("doc.docx") is False
