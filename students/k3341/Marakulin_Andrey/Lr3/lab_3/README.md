# Лабораторная работа 3

Тема: упаковка FastAPI-приложения в Docker, подключение отдельного сервиса парсера и запуск парсинга через очередь Celery + Redis.

## Состав проекта

```text
lab_3/
  app/
    lab2_parser_adapter.py
    routers/parser.py
    parser.py
    celery_app.py
    tasks.py
  parser_service/
    main.py
  migrations/
    versions/0001_initial_personal_finance.py
    versions/0002_add_parsed_sources.py
  Dockerfile
  docker-compose.yml
  requirements.txt
```

Проект является развитием лабораторных работ 1 и 2. Из лабораторной работы 1 используется FastAPI-приложение с доменной моделью личных финансов, PostgreSQL и миграциями Alembic. Из лабораторной работы 2 используется логика загрузки HTML и извлечения `<title>`; она вынесена в модуль `app/lab2_parser_adapter.py` и подключена к Docker/Celery-инфраструктуре лабораторной работы 3.

Результаты парсинга сохраняются отдельно от финансовых категорий, в таблицу `parsedsource`, и привязываются к авторизованному пользователю. Запись результатов в PostgreSQL выполняется через `AsyncSession` и `async_sessionmaker`, по аналогии с асинхронным сохранением из лабораторной работы 2.

## Запуск

```bash
docker compose up --build
```

После запуска доступны:

- FastAPI: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Parser service: `http://localhost:8001/health`
- PostgreSQL: `localhost:5434`
- Redis: `localhost:6379`

## Проверка через API

Зарегистрировать пользователя:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"demo@example.com\",\"username\":\"demo\",\"password\":\"demo12345\"}"
```

Получить токен:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo12345"
```

Дальше в командах вместо `<token>` нужно подставить `access_token`.

Прямой вызов парсера через отдельный parser-контейнер:

```bash
curl -X POST http://localhost:8000/parser/sync \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://www.cbr.ru/eng/key-indicators/\"}"
```

Вызов парсера через очередь Celery:

```bash
curl -X POST http://localhost:8000/parser/queue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://www.moex.com/en/\"}"
```

Проверить статус задачи:

```bash
curl http://localhost:8000/parser/tasks/<task_id> \
  -H "Authorization: Bearer <token>"
```

Посмотреть сохраненные результаты парсинга текущего пользователя:

```bash
curl http://localhost:8000/parser/sources \
  -H "Authorization: Bearer <token>"
```

## Реализованные требования

- FastAPI-приложение упаковано в Docker.
- Код FastAPI, моделей и миграций из лабораторной работы 1 переиспользован как основа приложения.
- Код парсинга из лабораторной работы 2 адаптирован в модуле `app/lab2_parser_adapter.py`.
- PostgreSQL запускается как отдельный сервис в Docker Compose.
- Парсер вынесен в отдельный контейнер `parser`.
- Добавлен API-эндпоинт для прямого вызова парсера: `POST /parser/sync`.
- Добавлены Redis и Celery worker.
- Добавлены API-эндпоинты для очереди: `POST /parser/queue`, `GET /parser/tasks/{task_id}`.
- Результаты парсинга асинхронно сохраняются в отдельную таблицу `parsedsource`, а не смешиваются с категориями личных финансов.
- Эндпоинты парсинга доступны только авторизованному пользователю.
