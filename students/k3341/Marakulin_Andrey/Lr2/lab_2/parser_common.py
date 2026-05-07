from __future__ import annotations

import argparse
import gzip
import html
import sys
import time
import urllib.request
import zlib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


STUDENT_DIR = Path(__file__).resolve().parents[2]
LAB1_DIR = STUDENT_DIR / "Lr1" / "lab_1"
if str(LAB1_DIR) not in sys.path:
    sys.path.insert(0, str(LAB1_DIR))

from sqlalchemy.exc import IntegrityError  # noqa: E402
from sqlmodel import SQLModel, Session, select  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db import engine  # noqa: E402
from app.models import Category, User  # noqa: E402


DEFAULT_URLS = [
    "https://www.cbr.ru/eng/key-indicators/",
    "https://www.cbr.ru/eng/currency_base/daily/",
    "https://www.moex.com/en/",
    "https://finance.yahoo.com/markets/",
    "https://www.investing.com/",
]


@dataclass(frozen=True)
class ParsedPage:
    url: str
    title: str
    category_id: int | None
    elapsed: float


class TitleParser(HTMLParser):
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


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("urls", nargs="*", default=DEFAULT_URLS)
    return parser


def extract_title(document: str, url: str) -> str:
    parser = TitleParser()
    parser.feed(document)
    title = html.unescape(parser.title)
    if title:
        return " ".join(title.split())
    return urlparse(url).netloc or url


def fetch_html(url: str, timeout: float = 15.0) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "itmo-lab2-parser/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw_document = response.read()
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        if content_encoding == "gzip":
            raw_document = gzip.decompress(raw_document)
        elif content_encoding == "deflate":
            raw_document = zlib.decompress(raw_document)
        return raw_document.decode(charset, errors="replace")


def ensure_parser_user(session: Session) -> User:
    email = "lab2-parser@example.com"
    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        return user

    user = User(
        email=email,
        username="lab2_parser",
        hashed_password=hash_password("lab2_parser_password"),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing_user = session.exec(select(User).where(User.email == email)).first()
        if existing_user:
            return existing_user
        raise
    session.refresh(user)
    return user


def initialize_database() -> None:
    SQLModel.metadata.create_all(engine)


def save_title(url: str, title: str, method: str) -> int | None:
    with Session(engine) as session:
        user = ensure_parser_user(session)
        category = Category(
            title=f"{method} financial source: {title}"[:100],
            description=f"Financial source parsed from {url}"[:255],
            user_id=user.id,
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        return category.id


def parse_and_save_sync(url: str, method: str) -> ParsedPage:
    started_at = time.perf_counter()
    document = fetch_html(url)
    title = extract_title(document, url)
    category_id = save_title(url, title, method)
    return ParsedPage(
        url=url,
        title=title,
        category_id=category_id,
        elapsed=time.perf_counter() - started_at,
    )


def print_pages(method: str, pages: list[ParsedPage], started_at: float) -> None:
    print(f"Method: {method}")
    for page in pages:
        print(
            f"{page.url} -> {page.title} "
            f"(category_id={page.category_id}, elapsed={page.elapsed:.3f}s)"
        )
    print(f"Total elapsed: {time.perf_counter() - started_at:.6f} seconds")
