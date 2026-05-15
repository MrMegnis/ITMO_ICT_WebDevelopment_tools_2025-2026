# Лабораторная работа 3. Docker, источники данных и очереди

## Информация о работе

| Параметр | Значение |
|----------|----------|
| Студент | Маракулин Андрей |
| Группа | К3341 |
| Тема | Упаковка FastAPI в Docker, отдельный сервис парсера, Celery + Redis |
| Формат | FastAPI + PostgreSQL + Docker Compose + Celery + Redis |
| Статус | Выполнена |

## Ссылки на исходный код

- Репозиторий: [ITMO_ICT_WebDevelopment_tools_2025-2026](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026)
- Лабораторная работа: [lab_3](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Marakulin_Andrey/Lr3/lab_3)

## Цель работы

Научиться упаковывать FastAPI-приложение в Docker, запускать приложение вместе с базой данных через Docker Compose, подключать отдельный сервис парсинга данных и выполнять парсинг как напрямую через API, так и асинхронно через очередь задач.

## Структура проекта

```text
lab_3/
  app/
    lab2_parser_adapter.py
    routers/parser.py
    celery_app.py
    parser.py
    tasks.py
    main.py
  parser_service/main.py
  migrations/
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
```

Лабораторная работа 3 является развитием лабораторных работ 1 и 2. Из лабораторной работы 1 используется FastAPI-приложение с моделями личных финансов, PostgreSQL и миграциями Alembic. Из лабораторной работы 2 используется логика парсинга HTML-страниц и извлечения `<title>`, адаптированная в модуле `app/lab2_parser_adapter.py`.

В лабораторной работе 3 этот код упакован в Docker-инфраструктуру, дополнен отдельным parser-сервисом и очередью задач Celery + Redis.

## Подзадача 1. Упаковка FastAPI, БД и парсера в Docker

Для проекта создан `Dockerfile`, который собирает Python-образ, устанавливает зависимости из `requirements.txt` и копирует код приложения.

В `docker-compose.yml` описаны сервисы:

| Сервис | Назначение |
| --- | --- |
| `postgres` | база данных PostgreSQL для приложения |
| `api` | основное FastAPI-приложение |
| `parser` | отдельный FastAPI-сервис парсера |
| `redis` | брокер сообщений и backend результатов Celery |
| `worker` | Celery worker для фонового парсинга |

Контейнер `api` перед стартом выполняет миграции Alembic:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Подзадача 2. Вызов парсера из FastAPI

В основном API добавлен роутер `app/routers/parser.py`.

Прямой вызов:

```http
POST /parser/sync
```

Тело запроса:

```json
{
  "url": "https://www.cbr.ru/eng/key-indicators/"
}
```

Эндпоинт требует JWT-авторизацию. Основное API передает URL и `user_id` текущего пользователя в отдельный parser-сервис по адресу из `PARSER_SERVICE_URL`.

Parser-сервис использует адаптированную логику из лабораторной работы 2: загружает HTML-страницу, извлекает содержимое тега `<title>` и асинхронно сохраняет результат в таблицу `parsedsource` через `AsyncSession`. Результаты парсинга не смешиваются с финансовыми категориями пользователя.

## Подзадача 3. Вызов парсера через очередь

Для фонового запуска добавлены Redis и Celery.

Конфигурация Celery находится в `app/celery_app.py`, задача парсинга определена в `app/tasks.py`:

```python
@celery_app.task(name="parser.parse_url")
def parse_url_task(url: str, user_id: int) -> dict[str, str | int | float | None]:
    return parse_and_save(url, user_id=user_id, source="celery").as_dict()
```

Эндпоинт постановки задачи:

```http
POST /parser/queue
```

Эндпоинт проверки статуса:

```http
GET /parser/tasks/{task_id}
```

Список сохраненных результатов текущего пользователя:

```http
GET /parser/sources
```

## Общая логика парсера

Логика парсинга из лабораторной работы 2 вынесена в `app/lab2_parser_adapter.py`:

- загрузка HTML через `urllib.request`;
- поддержка `gzip` и `deflate`;
- извлечение `<title>` через стандартный `HTMLParser`;

Логика лабораторной работы 3 находится в `app/parser.py`:

- асинхронное сохранение результата в таблицу `parsedsource` через `async_sessionmaker`;
- привязка результата к авторизованному пользователю.

## Запуск проекта

```bash
cd students/k3341/Marakulin_Andrey/Lr3/lab_3
docker compose up --build
```

После запуска доступны:

- Swagger основного API: `http://localhost:8000/docs`
- healthcheck parser-сервиса: `http://localhost:8001/health`
- PostgreSQL: `localhost:5434`
- Redis: `localhost:6379`

## Проверка запросов

Сначала нужно зарегистрировать пользователя и получить JWT-токен.

Регистрация:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"demo@example.com\",\"username\":\"demo\",\"password\":\"demo12345\"}"
```

Авторизация:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo12345"
```

Прямой вызов парсера:

```bash
curl -X POST http://localhost:8000/parser/sync \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://www.cbr.ru/eng/key-indicators/\"}"
```

Вызов через очередь:

```bash
curl -X POST http://localhost:8000/parser/queue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://www.moex.com/en/\"}"
```

Проверка задачи:

```bash
curl http://localhost:8000/parser/tasks/<task_id> \
  -H "Authorization: Bearer <token>"
```

Проверка сохраненных результатов:

```bash
curl http://localhost:8000/parser/sources \
  -H "Authorization: Bearer <token>"
```
## Вывод

В ходе лабораторной работы код из предыдущих работ был объединен в единую инфраструктуру: FastAPI-приложение и база данных из лабораторной работы 1 были перенесены в Docker, а парсер из лабораторной работы 2 был подключен как отдельный сервис и как Celery-задача. Результаты парсинга сохраняются в отдельной доменной таблице и доступны только пользователю, который запустил обработку.
