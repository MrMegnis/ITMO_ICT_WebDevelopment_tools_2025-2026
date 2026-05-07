from __future__ import annotations

import multiprocessing
import time

from parser_common import ParsedPage, build_parser, initialize_database, parse_and_save_sync, print_pages


def parse_and_save(url: str) -> ParsedPage:
    return parse_and_save_sync(url, "multiprocessing")


def main() -> None:
    parser = build_parser("Parse pages in parallel with multiprocessing.")
    args = parser.parse_args()

    started_at = time.perf_counter()
    initialize_database()
    with multiprocessing.Pool(processes=min(len(args.urls), multiprocessing.cpu_count())) as pool:
        results = pool.map(parse_and_save, args.urls)

    print_pages("multiprocessing", results, started_at)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
