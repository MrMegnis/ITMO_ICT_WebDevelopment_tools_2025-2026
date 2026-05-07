from __future__ import annotations

import multiprocessing
import time

from sum_common import build_parser, calculate_sum as calculate_range_sum, print_result, split_ranges


def calculate_sum(start: int, end: int) -> int:
    return calculate_range_sum(start, end)


def calculate_sum_for_range(bounds: tuple[int, int]) -> int:
    start, end = bounds
    return calculate_sum(start, end)


def main() -> None:
    parser = build_parser("Calculate a sum with multiprocessing.")
    args = parser.parse_args()

    ranges = split_ranges(args.limit, args.workers)
    started_at = time.perf_counter()

    with multiprocessing.Pool(processes=args.workers) as pool:
        results = pool.map(calculate_sum_for_range, ranges)

    print_result("multiprocessing", args.limit, args.workers, results, started_at)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
