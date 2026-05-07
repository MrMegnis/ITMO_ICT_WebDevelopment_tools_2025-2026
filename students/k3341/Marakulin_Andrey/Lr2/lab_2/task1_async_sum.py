from __future__ import annotations

import asyncio
import time

from sum_common import build_parser, calculate_sum as calculate_range_sum, print_result, split_ranges


def calculate_sum(start: int, end: int) -> int:
    return calculate_range_sum(start, end)


async def calculate_sum_async(start: int, end: int) -> int:
    await asyncio.sleep(0)
    return calculate_sum(start, end)


async def run(limit: int, workers: int) -> list[int]:
    tasks = [calculate_sum_async(start, end) for start, end in split_ranges(limit, workers)]
    return list(await asyncio.gather(*tasks))


def main() -> None:
    parser = build_parser("Calculate a sum with asyncio.")
    args = parser.parse_args()

    started_at = time.perf_counter()
    results = asyncio.run(run(args.limit, args.workers))
    print_result("asyncio", args.limit, args.workers, results, started_at)


if __name__ == "__main__":
    main()
