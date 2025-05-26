from urllib.parse import urlparse, urlencode, urljoin, unquote
import html
import re


def _url_seg(url: str):
    """
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    :param url:
    :return:
    """
    seg = urlparse(url)
    return [seg.scheme, seg.netloc, seg.path, seg.params, seg.query]


def url_path(url: str):
    return _url_seg(url)[2]


def replace_url_host(url: str, host: str) -> str:
    seg = _url_seg(url)
    return url.replace(seg[1], host)


def valid_url(url: str) -> bool:
    try:
        return all(_url_seg(url)[:2])
    except Exception:
        return False


def valid_url_no_sche(url: str) -> bool:
    return _url_seg(url)[2] != ""


def url_host(url: str) -> str:
    seg = _url_seg(url)
    return f"{seg[0]}://{seg[1]}"


def same_host_url(u1, u2) -> bool:
    if not valid_url(u1) or not valid_url(u2):
        return False
    return _url_seg(u1)[1] == _url_seg(u2)[1]


def same_url(u1, u2) -> bool:
    u1 = url_to_cn(u1)
    u2 = url_to_cn(u2)
    if not valid_url(u1) or not valid_url(u2):
        return False
    s2 = _url_seg(u2)
    for i, s in enumerate(_url_seg(u1)):
        if s != s2[i]:
            # print(f"same url {s} {s2[i]}")
            return False
    return True


def url_missing(url: str) -> bool:
    """
    url缺少host，可以尝试补全下
    """
    seg = _url_seg(url)
    return not seg[0] and not seg[1]


def get_url(full_u: str, href: str) -> str:
    return urljoin(url_host(full_u), href)


def html_encode(s: str) -> str:
    return html.escape(s)


def html_decode(s: str) -> str:
    return html.unescape(s)


def url_to_cn(s: str) -> str:
    return unquote(s)


def url_filename(url: str) -> str:
    return urlparse(url.rsplit('/', 1)[-1]).path


_UrlRegex = re.compile("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")


def pick_url(s: str) -> str:
    match = _UrlRegex.search(s)
    return match


def url_last_name(url: str):
    return url.rsplit('/', 1)[1]


def dict_to_param(data: dict):
    return urlencode(data)
