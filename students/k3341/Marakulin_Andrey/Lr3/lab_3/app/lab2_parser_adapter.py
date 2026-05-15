from __future__ import annotations

import gzip
import html
import urllib.request
import zlib
from html.parser import HTMLParser
from urllib.parse import urlparse


class TitleParser(HTMLParser):
    """Title extractor adapted from Lr2/lab_2/parser_common.py."""

    def __init__(self) -> None:
        super().__init__()
        self._inside_title = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._inside_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self._chunks.append(data.strip())

    @property
    def title(self) -> str:
        return " ".join(chunk for chunk in self._chunks if chunk).strip()


def fetch_html(url: str, timeout: float = 15.0) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "itmo-lab2-parser-adapted-for-lab3/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        document = response.read()
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        if content_encoding == "gzip":
            document = gzip.decompress(document)
        elif content_encoding == "deflate":
            document = zlib.decompress(document)
        return document.decode(charset, errors="replace")


def extract_title(document: str, url: str) -> str:
    parser = TitleParser()
    parser.feed(document)
    title = html.unescape(parser.title)
    if title:
        return " ".join(title.split())
    return urlparse(url).netloc or url
