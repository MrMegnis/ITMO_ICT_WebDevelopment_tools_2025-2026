from __future__ import annotations

import threading
import time

from parser_common import ParsedPage, build_parser, initialize_database, parse_and_save_sync, print_pages


def parse_and_save(url: str) -> ParsedPage:
    return parse_and_save_sync(url, "threading")


def main() -> None:
    parser = build_parser("Parse pages in parallel with threading.")
    args = parser.parse_args()

    results: list[ParsedPage | None] = [None] * len(args.urls)
    threads: list[threading.Thread] = []
    started_at = time.perf_counter()
    initialize_database()

    for index, url in enumerate(args.urls):
        thread = threading.Thread(
            target=lambda i=index, current_url=url: results.__setitem__(i, parse_and_save(current_url)),
            name=f"parser-thread-{index + 1}",
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print_pages("threading", [page for page in results if page is not None], started_at)


if __name__ == "__main__":
    main()
