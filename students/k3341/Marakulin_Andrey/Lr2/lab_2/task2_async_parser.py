from __future__ import annotations

import asyncio
import sys
import time

import aiohttp

from parser_common import (
    ParsedPage,
    build_parser,
    extract_title,
    initialize_database_async,
    print_pages,
    save_title_async,
)


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def fetch_html(session, url: str) -> str:
    async with session.get(url, timeout=15) as response:
        response.raise_for_status()
        return await response.text()


async def parse_and_save(url: str) -> ParsedPage:
    started_at = time.perf_counter()
    async with aiohttp.ClientSession(headers={"User-Agent": "itmo-lab2-parser/1.0"}) as session:
        document = await fetch_html(session, url)
    title = extract_title(document, url)
    category_id = await save_title_async(url, title, "asyncio")
    return ParsedPage(
        url=url,
        title=title,
        category_id=category_id,
        elapsed=time.perf_counter() - started_at,
    )


async def run(urls: list[str]) -> list[ParsedPage]:
    await initialize_database_async()
    return list(await asyncio.gather(*(parse_and_save(url) for url in urls)))


def main() -> None:
    parser = build_parser("Parse pages in parallel with asyncio and aiohttp.")
    args = parser.parse_args()

    started_at = time.perf_counter()
    results = asyncio.run(run(args.urls))
    print_pages("asyncio", results, started_at)


if __name__ == "__main__":
    main()
