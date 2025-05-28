import smartutils.data.url as url_mod

def test_url_module():
    url = "http://example.com:8080/path/file.html?x=1#frag"
    assert url_mod.url_path(url) == "/path/file.html"
    assert url_mod.replace_url_host(url, "test.com:80").startswith("http://test.com:80")
    assert url_mod.is_valid_url(url)
    assert not url_mod.is_valid_url(123)
    assert url_mod.has_url_path(url)
    assert url_mod.url_host(url) == "http://example.com:8080"
    assert url_mod.is_same_host(url, url)
    assert url_mod.is_same_url(url, url)
    assert url_mod.is_url_missing_host("/path")
    assert url_mod.resolve_relative_url(url, "/other") == "http://example.com:8080/other"
    assert url_mod.html_encode("<>") == "&lt;&gt;"
    assert url_mod.html_decode("&lt;&gt;") == "<>"
    assert url_mod.url_decode("a%20b") == "a b"
    assert url_mod.url_filename(url) == "file.html"
    assert url_mod.find_url_in_text("see http://a.com") == "http://a.com"
    assert url_mod.url_last_segment(url) == "file.html"
    assert url_mod.dict_to_query_params({"a":1}) == "a=1"

def test_url_edge_cases():
    # is_valid_url
    assert not url_mod.is_valid_url("")
    assert not url_mod.is_valid_url(None)
    assert not url_mod.is_valid_url("/path")
    # find_url_in_text
    assert url_mod.find_url_in_text("no url here") is None
    assert url_mod.find_url_in_text("http://a.com and http://b.com").startswith("http://")
    # 其他边界
    assert url_mod.url_path("") == ""
    assert url_mod.url_host("") == ""
    assert url_mod.replace_url_host("http://a.com/x", "b.com") == "http://b.com/x"
    assert url_mod.url_filename("") == ""
    assert url_mod.url_last_segment("") == ""
    assert url_mod.dict_to_query_params({}) == ""