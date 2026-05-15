import asyncio
import time
from dataclasses import dataclass

from app.db import AsyncSessionLocal
from app.lab2_parser_adapter import extract_title, fetch_html
from app.models import ParsedSource


@dataclass(frozen=True)
class ParsedPage:
    url: str
    title: str
    parsed_source_id: int | None
    elapsed: float

    def as_dict(self) -> dict[str, str | int | float | None]:
        return {
            "url": self.url,
            "title": self.title,
            "parsed_source_id": self.parsed_source_id,
            "elapsed": self.elapsed,
        }


async def save_parsed_page_async(
    url: str,
    title: str,
    source: str,
    user_id: int,
    elapsed: float,
) -> int | None:
    async with AsyncSessionLocal() as session:
        parsed_source = ParsedSource(
            url=url[:2048],
            title=title[:255],
            source=source[:50],
            elapsed=elapsed,
            user_id=user_id,
        )
        session.add(parsed_source)
        await session.commit()
        await session.refresh(parsed_source)
        return parsed_source.id


async def parse_and_save_async(url: str, user_id: int, source: str = "lab3") -> ParsedPage:
    started_at = time.perf_counter()
    document = fetch_html(url)
    title = extract_title(document, url)
    elapsed = time.perf_counter() - started_at
    parsed_source_id = await save_parsed_page_async(url, title, source, user_id, elapsed)
    return ParsedPage(
        url=url,
        title=title,
        parsed_source_id=parsed_source_id,
        elapsed=elapsed,
    )


def parse_and_save(url: str, user_id: int, source: str = "lab3") -> ParsedPage:
    return asyncio.run(parse_and_save_async(url, user_id=user_id, source=source))
