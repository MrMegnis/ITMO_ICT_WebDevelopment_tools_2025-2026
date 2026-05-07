from __future__ import annotations

import asyncio
import time

from parser_common import ParsedPage, build_parser, extract_title, initialize_database, print_pages, save_title


async def fetch_html(session, url: str) -> str:
    async with session.get(url, timeout=15) as response:
        response.raise_for_status()
        return await response.text()


async def parse_and_save(url: str) -> ParsedPage:
    import aiohttp

    started_at = time.perf_counter()
    async with aiohttp.ClientSession(headers={"User-Agent": "itmo-lab2-parser/1.0"}) as session:
        document = await fetch_html(session, url)
    title = extract_title(document, url)
    category_id = await asyncio.to_thread(save_title, url, title, "asyncio")
    return ParsedPage(
        url=url,
        title=title,
        category_id=category_id,
        elapsed=time.perf_counter() - started_at,
    )


async def run(urls: list[str]) -> list[ParsedPage]:
    return list(await asyncio.gather(*(parse_and_save(url) for url in urls)))


def main() -> None:
    parser = build_parser("Parse pages in parallel with asyncio and aiohttp.")
    args = parser.parse_args()

    started_at = time.perf_counter()
    initialize_database()
    results = asyncio.run(run(args.urls))
    print_pages("asyncio", results, started_at)


if __name__ == "__main__":
    main()
