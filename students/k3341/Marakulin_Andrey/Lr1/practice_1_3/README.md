# Практика 1.3 - Миграции, .env и .gitignore (Personal Finance API)

В этой практике на базе `practice_1_2` добавлены:

- поддержка `.env` для URL базы данных (`DB_ADMIN`);
- `.gitignore` с исключением `*.env` и служебных файлов;
- настройка Alembic для SQLModel;
- миграция, добавляющая поле `level` в таблицу связи `transactiontaglink`.

## Структура

- `app/models.py` - модели SQLModel (в `TransactionTagLink` добавлено поле `level`)
- `app/connection.py` - загрузка переменных окружения и подключение к БД
- `migrations/` - конфигурация и версии миграций Alembic
- `.env` - строка подключения к БД
- `.gitignore` - игнорируемые файлы проекта

## Запуск

1. Установка зависимостей:

```bash
pip install fastapi uvicorn sqlmodel alembic python-dotenv
```

2. Генерация миграции (уже выполнено в рамках практики):

```bash
alembic revision --autogenerate -m "add level to transaction-tag link"
```

3. Применение миграции:

```bash
alembic upgrade head
```

4. Запуск API:

```bash
uvicorn app.main:app --reload
```
