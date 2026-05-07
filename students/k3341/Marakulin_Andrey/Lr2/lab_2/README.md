# Laboratory work 2 - Threads, processes and async Python

The work contains six Python programs:

- `task1_threading_sum.py` - splits the sum from `1` to `10_000_000_000_000` between threads.
- `task1_multiprocessing_sum.py` - solves the same task with worker processes.
- `task1_async_sum.py` - solves the same task with `asyncio` tasks.
- `task2_threading_parser.py` - parses page titles in threads and saves them to the Lab 1 database.
- `task2_multiprocessing_parser.py` - parses page titles in processes and saves them to the Lab 1 database.
- `task2_async_parser.py` - parses page titles with `asyncio` and `aiohttp`, then saves them to the Lab 1 database.

The Lab 1 project is a personal finance API, so the parser works with financial web pages:
central bank indicators, exchange rates, stock market and investing pages. Parsed page titles are
stored in the existing `category` table as financial information sources. The parser creates a
technical user `lab2-parser@example.com` and creates one category per parsed page. The category
description contains the source URL.

## Setup

Run commands from `students/k3341/Marakulin_Andrey/Lr2/lab_2`.

```bash
pip install -r requirements.txt
```

Start PostgreSQL from Lab 1 before running parser scripts:

```bash
cd ../../Lr1/lab_1
docker compose up -d
alembic upgrade head
cd ../../Lr2/lab_2
```

If PostgreSQL dependencies are not available, the Lab 1 code has a SQLite fallback. PostgreSQL is
still the recommended option because multiprocessing writes are safer with a real database server.

## Task 1: sum programs

Full task value:

```bash
python task1_threading_sum.py
python task1_multiprocessing_sum.py
python task1_async_sum.py
```

Fast demo value:

```bash
python task1_threading_sum.py --limit 1000000 --workers 4
python task1_multiprocessing_sum.py --limit 1000000 --workers 4
python task1_async_sum.py --limit 1000000 --workers 4
```

Each program has a `calculate_sum()` function. The calculation uses the arithmetic progression
formula for every range, because iterating to `10_000_000_000_000` directly is not practical.

## Task 2: parser programs

Default financial URLs are included in `parser_common.py`.

```bash
python task2_threading_parser.py
python task2_multiprocessing_parser.py
python task2_async_parser.py
```

Custom URLs can be passed as positional arguments:

```bash
python task2_async_parser.py https://www.cbr.ru/eng/key-indicators/ https://www.moex.com/en/
```

Each parser program has a `parse_and_save(url)` function. It downloads HTML, extracts the
`<title>` tag, saves the result to the Lab 1 database and prints the saved category id. The saved
row is connected with the personal finance domain: the page title becomes a financial source in
the existing `category` table, and the original URL is saved in `description`.

## Comparison

Sample command for Task 1:

```bash
python task1_threading_sum.py --limit 1000000 --workers 4
```

| Program | Best use case | Expected result |
| --- | --- | --- |
| threading | I/O-bound tasks, such as web requests | Simple to write, but CPU-bound Python code is limited by the GIL |
| multiprocessing | CPU-bound calculations | Uses several CPU cores, but process startup and data transfer add overhead |
| asyncio | Many waiting operations, such as HTTP requests | Very efficient for I/O-bound work, but CPU-bound work does not become faster by itself |

For Task 1 all three variants are fast because every worker uses a formula. With a real loop,
`multiprocessing` would usually be faster for CPU-bound work, while `threading` and `asyncio`
would not bypass the GIL.

For Task 2, `threading` and `asyncio` are both good choices because most time is spent waiting for
network responses. `multiprocessing` also works, but it spends more resources on processes and is
usually unnecessary for HTTP parsing.

## Result table template

Fill the table with times from your machine after running the scripts.

| Task | threading | multiprocessing | asyncio |
| --- | ---: | ---: | ---: |
| Sum, `--limit 1000000 --workers 4` | 0.001848 s | 0.234405 s | 0.002962 s |
| Parser, default URLs | 0.994758 s | 1.537587 s | 0.953795 s |
