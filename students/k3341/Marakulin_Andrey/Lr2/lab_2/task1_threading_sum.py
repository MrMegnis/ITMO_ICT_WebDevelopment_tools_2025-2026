from __future__ import annotations

import threading
import time

from sum_common import build_parser, calculate_sum as calculate_range_sum, print_result, split_ranges


def calculate_sum(start: int, end: int) -> int:
    return calculate_range_sum(start, end)


def main() -> None:
    parser = build_parser("Calculate a sum with threading.")
    args = parser.parse_args()

    ranges = split_ranges(args.limit, args.workers)
    results = [0] * len(ranges)
    threads: list[threading.Thread] = []

    started_at = time.perf_counter()

    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(
            target=lambda i=index, s=start, e=end: results.__setitem__(i, calculate_sum(s, e)),
            name=f"sum-thread-{index + 1}",
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print_result("threading", args.limit, args.workers, results, started_at)


if __name__ == "__main__":
    main()
