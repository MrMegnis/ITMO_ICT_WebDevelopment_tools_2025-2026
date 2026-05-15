from __future__ import annotations

import argparse
import os
import time
from collections.abc import Iterable


DEFAULT_LIMIT = 10_000_000_000_000
DEFAULT_WORKERS = max(2, min(8, os.cpu_count() or 2))


def split_ranges(limit: int, workers: int) -> list[tuple[int, int]]:
    chunk_size = limit // workers
    ranges: list[tuple[int, int]] = []
    start = 1

    for worker_index in range(workers):
        end = start + chunk_size - 1
        if worker_index == workers - 1:
            end = limit
        ranges.append((start, end))
        start = end + 1

    return ranges


def calculate_sum(start: int, end: int) -> int:
    total = 0
    for number in range(start, end + 1):
        total += number
    return total


def expected_sum(limit: int) -> int:
    return limit * (limit + 1) // 2


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    return parser


def print_result(method: str, limit: int, workers: int, parts: Iterable[int], started_at: float) -> None:
    total = sum(parts)
    elapsed = time.perf_counter() - started_at
    print(f"Method: {method}")
    print(f"Limit: {limit}")
    print(f"Workers: {workers}")
    print(f"Result: {total}")
    print(f"Expected: {expected_sum(limit)}")
    print(f"Correct: {total == expected_sum(limit)}")
    print(f"Elapsed: {elapsed:.6f} seconds")
