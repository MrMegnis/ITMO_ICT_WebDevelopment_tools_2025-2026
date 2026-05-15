# Лабораторная работа 2. Потоки. Процессы. Асинхронность

## Информация о работе

| Параметр | Значение |
|----------|----------|
| Студент | Маракулин Андрей |
| Группа | К3341 |
| Тема | Потоки, процессы и асинхронное программирование в Python |
| Формат | `threading` + `multiprocessing` + `asyncio` |
| Задания | Расчет суммы и асинхронный/параллельный парсер |

## Ссылки на исходный код

- Репозиторий: [ITMO_ICT_WebDevelopment_tools_2025-2026](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026)
- Лабораторная работа: [lab_2](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Marakulin_Andrey/Lr2/lab_2)

## Цель работы

Изучить способы параллельного и асинхронного выполнения задач в Python, сравнить подходы `threading`, `multiprocessing` и `asyncio` на двух типах задач:
- вычислительная задача: подсчет суммы чисел от `1` до `10_000_000_000_000`;
- I/O-задача: загрузка веб-страниц, извлечение заголовков `<title>` и сохранение результатов в базу данных из лабораторной работы 1.

## Структура проекта

```text
lab_2/
  README.md
  requirements.txt
  sum_common.py
  parser_common.py
  task1_threading_sum.py
  task1_multiprocessing_sum.py
  task1_async_sum.py
  task2_threading_parser.py
  task2_multiprocessing_parser.py
  task2_async_parser.py
  __init__.py
```

Общая логика вынесена в отдельные модули:
- `sum_common.py` содержит разбиение диапазона, расчет суммы обычным циклом, расчет ожидаемого значения и вывод результата;
- `parser_common.py` содержит список URL, загрузку HTML через стандартную библиотеку, извлечение тега `<title>`, инициализацию БД и сохранение результата в таблицу `category` проекта из лабораторной работы 1.

## Задание 1. Расчет суммы

В первом задании реализованы три программы, которые считают сумму чисел от `1` до заданного предела. По умолчанию используется значение `10_000_000_000_000`, но для быстрой проверки можно передать меньший предел через аргумент `--limit`.

### Общий алгоритм

Диапазон чисел разбивается на части по количеству исполнителей:

```python
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
```

Сумма внутри каждого диапазона считается обычным циклом:

```python
def calculate_sum(start: int, end: int) -> int:
    total = 0
    for number in range(start, end + 1):
        total += number
    return total
```

Такой подход делает задачу CPU-bound и позволяет сравнить потоки, процессы и `asyncio` на реальном вычислении. Полный предел `10_000_000_000_000` слишком велик для живой демонстрации, поэтому для проверки используется уменьшенный `--limit`.

### Реализация через `threading`

Файл: `task1_threading_sum.py`

Для каждой части диапазона создается отдельный поток `threading.Thread`. Результаты сохраняются в общий список, после чего основной поток ожидает завершения всех потоков через `join()`.

Особенность подхода: потоки удобны для задач ожидания ввода-вывода, но для CPU-bound вычислений в Python ограничены GIL.

### Реализация через `multiprocessing`

Файл: `task1_multiprocessing_sum.py`

Диапазоны передаются в пул процессов `multiprocessing.Pool`, а результаты собираются через `pool.map()`.

Особенность подхода: процессы позволяют использовать несколько ядер CPU и подходят для тяжелых вычислений. Недостаток - дополнительные затраты на запуск процессов и передачу данных между ними.

### Реализация через `asyncio`

Файл: `task1_async_sum.py`

Для каждой части диапазона создается асинхронная задача, а результаты собираются через `asyncio.gather()`.

Особенность подхода: `asyncio` хорошо подходит для большого количества операций ожидания, но сам по себе не ускоряет CPU-bound вычисления. В этой задаче он используется для демонстрации асинхронной организации выполнения.

## Задание 2. Парсер веб-страниц

Во втором задании реализованы три варианта парсера, который:
- получает HTML-документ по URL;
- извлекает содержимое тега `<title>`;
- создает технического пользователя `lab2-parser@example.com`;
- сохраняет заголовок страницы в таблицу `category` базы данных из лабораторной работы 1;
- записывает исходный URL в поле `description`.

Для парсинга выбраны финансовые страницы, так как проект из лабораторной работы 1 посвящен сервису управления личными финансами:
- `https://www.cbr.ru/eng/key-indicators/`
- `https://www.cbr.ru/eng/currency_base/daily/`
- `https://www.moex.com/en/`
- `https://finance.yahoo.com/markets/`
- `https://www.investing.com/`

### Общая логика парсера

В `parser_common.py` реализован HTML-парсер на основе стандартного `HTMLParser`:

```python
class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._inside_title = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._inside_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self._chunks.append(data.strip())
```

Сохранение выполняется через модели и подключение из лабораторной работы 1:

```python
category = Category(
    title=f"{method} financial source: {title}"[:100],
    description=f"Financial source parsed from {url}"[:255],
    user_id=user.id,
)
```

Таким образом, лабораторная работа 2 не использует отдельную базу, а интегрируется с уже созданным FastAPI-проектом.

### Реализация через `threading`

Файл: `task2_threading_parser.py`

Для каждого URL создается поток. Каждый поток вызывает `parse_and_save()`, загружает страницу и сохраняет результат в БД. Основной поток ожидает завершения всех рабочих потоков.

Такой подход хорошо подходит для сетевого парсинга, потому что основное время уходит на ожидание ответа от сайтов.

### Реализация через `multiprocessing`

Файл: `task2_multiprocessing_parser.py`

URL распределяются между процессами через `multiprocessing.Pool`. Каждый процесс независимо загружает страницу, извлекает заголовок и выполняет запись в БД.

Подход рабочий, но для сетевого парсинга обычно избыточен: процессы потребляют больше ресурсов, чем потоки или асинхронные задачи.

### Реализация через `asyncio` и `aiohttp`

Файл: `task2_async_parser.py`

Асинхронная версия использует `aiohttp` для HTTP-запросов и `asyncio.gather()` для одновременного запуска задач. Запись в БД тоже выполняется асинхронно: для этого используется SQLAlchemy `AsyncSession`, `create_async_engine()` и функция `save_title_async()`.

```python
async def run(urls: list[str]) -> list[ParsedPage]:
    await initialize_database_async()
    return list(await asyncio.gather(*(parse_and_save(url) for url in urls)))
```

Этот вариант наиболее естественен для большого количества сетевых запросов: пока один запрос ожидает ответа, event loop переключается на другие задачи.

## Запуск проекта

Установка зависимостей:

```bash
cd students/k3341/Marakulin_Andrey/Lr2/lab_2
pip install -r requirements.txt
```

Перед запуском парсеров рекомендуется поднять PostgreSQL и применить миграции из лабораторной работы 1:

```bash
cd ../../Lr1/lab_1
docker compose up -d
alembic upgrade head
cd ../../Lr2/lab_2
```

Запуск программ для задания 1:

```bash
python task1_threading_sum.py
python task1_multiprocessing_sum.py
python task1_async_sum.py
```

Быстрый демонстрационный запуск:

```bash
python task1_threading_sum.py --limit 10000000 --workers 4
python task1_multiprocessing_sum.py --limit 10000000 --workers 4
python task1_async_sum.py --limit 10000000 --workers 4
```

Запуск программ для задания 2:

```bash
python task2_threading_parser.py
python task2_multiprocessing_parser.py
python task2_async_parser.py
```

Запуск с пользовательскими URL:

```bash
python task2_async_parser.py https://www.cbr.ru/eng/key-indicators/ https://www.moex.com/en/
```

## Результаты сравнения

Результаты демонстрационного запуска из README:

| Задача | `threading` | `multiprocessing` | `asyncio` |
| --- | ---: | ---: | ---: |
| Сумма, `--limit 10000000 --workers 4` | 0.251209 s | 0.193703 s | 0.251658 s |
| Парсер, URL по умолчанию | 0.994758 s | 1.537587 s | 0.953795 s |

По результатам видно:
- для задачи суммы используется прямой цикл, поэтому время зависит от размера диапазона;
- `multiprocessing` быстрее на вычислительной задаче, потому что распределяет работу между процессами и может использовать несколько ядер CPU;
- для парсинга `threading` и `asyncio` показывают близкие результаты, так как задача является I/O-bound;
- `asyncio` немного быстрее в приведенном запуске и лучше масштабируется при большом количестве сетевых запросов;
- `multiprocessing` для парсинга работает корректно, но расходует больше ресурсов и обычно не нужен для такой задачи.

## Проверка соответствия требованиям

- Реализация вычислительной задачи через `threading`: выполнено.
- Реализация вычислительной задачи через `multiprocessing`: выполнено.
- Реализация вычислительной задачи через `asyncio`: выполнено.
- Реализация парсера через `threading`: выполнено.
- Реализация парсера через `multiprocessing`: выполнено.
- Реализация парсера через `asyncio` и `aiohttp`: выполнено.
- Использование общей функции `calculate_sum()`: выполнено.
- Использование общей функции `parse_and_save()`: выполнено.
- Сохранение результатов парсинга в базу данных лабораторной работы 1: выполнено.
- Сравнение подходов по времени выполнения: выполнено.

## Вывод

В ходе лабораторной работы были реализованы и сравнены три модели конкурентного выполнения в Python: потоки, процессы и асинхронные задачи. Для вычислительной задачи наиболее подходящим подходом является `multiprocessing`, так как он позволяет использовать несколько ядер процессора. `threading` и `asyncio` не ускоряют CPU-bound вычисления из-за GIL и отсутствия операций ожидания. Для сетевого парсинга лучше подходят `threading` и `asyncio`, поскольку основное время тратится на ожидание HTTP-ответов. Асинхронная реализация с `aiohttp` и `AsyncSession` удобна для масштабирования на большое количество URL.
