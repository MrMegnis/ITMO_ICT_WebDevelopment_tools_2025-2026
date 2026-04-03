# Практика 1.2 - Personal Finance API (SQLModel)

Во второй практике реализован FastAPI-сервис с ORM `SQLModel`:

- подключение к БД (`connection.py`)
- инициализация таблиц при старте приложения
- CRUD для сущностей `Category`, `Tag`, `Transaction`
- связи:
  - `Category (1) -> (N) Transaction`
  - `Transaction (N) <-> (N) Tag` через `TransactionTagLink`
- вложенное отображение связей в `GET /transaction/{transaction_id}`

## Структура

- `app/models.py` - SQLModel-модели и схемы запросов/ответов
- `app/connection.py` - движок, инициализация и сессии БД
- `app/main.py` - FastAPI-маршруты

## Запуск

1. Установить зависимости:

```bash
pip install fastapi uvicorn sqlmodel
```

2. Опционально задать PostgreSQL:

```bash
set DATABASE_URL=postgresql+psycopg://postgres:password@localhost/personal_finance
```

Если `DATABASE_URL` не задан, используется SQLite-файл `personal_finance_pr2.db`.

3. Запустить приложение:

```bash
uvicorn app.main:app --reload
```
