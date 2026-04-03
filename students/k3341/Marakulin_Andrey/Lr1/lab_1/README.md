# Лабораторная работа 1 (15 баллов) - Personal Finance API

Реализован сервис управления личными финансами на FastAPI.

## Что реализовано

- Тема: **Разработка сервиса для управления личными финансами**
- 7 таблиц в БД PostgreSQL: `app_user`, `category`, `tag`, `transaction`, `transactiontaglink`, `budget`, `goal`
- Связи:
  - `one-to-many`: пользователь -> категории/транзакции/бюджеты/цели
  - `many-to-many`: транзакции <-> теги через `transactiontaglink`
- Ассоциативная сущность `transactiontaglink` содержит дополнительные поля связи:
  - `importance`
  - `tagged_reason`
- Полный CRUD для категорий, тегов, транзакций, бюджетов, целей
- JWT-аутентификация и пользовательский функционал:
  - регистрация
  - логин и выдача JWT
  - получение текущего пользователя
  - список пользователей
  - смена пароля
- Отчет `/reports/summary` по доходам, расходам, балансу и превышениям бюджета
- Миграции Alembic настроены и включены

## Структура

- `app/main.py` - точка входа FastAPI
- `app/models.py` - SQLModel-модели таблиц и связей
- `app/schemas.py` - Pydantic/SQLModel-схемы API
- `app/routers/` - роутеры по доменным областям
- `app/core/security.py` - ручная логика JWT (HS256) и хэширования пароля (PBKDF2)
- `app/db.py` - engine и сессии
- `migrations/` - конфигурация и версии Alembic

## Запуск

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Скопировать `.env.example` в `.env` и заполнить параметры PostgreSQL.

3. Применить миграции:

```bash
alembic upgrade head
```

4. Запустить API:

```bash
uvicorn app.main:app --reload
```

## PostgreSQL через Docker Compose

1. Запустить PostgreSQL:

```bash
docker compose up -d
```

2. Проверить, что контейнер поднялся:

```bash
docker compose ps
```

3. Подключение к БД из IDE/клиента:

- Host: `localhost`
- Port: `5432`
- Database: `personal_finance_lab1`
- User: `postgres`
- Password: `postgres`

4. Остановить контейнер:

```bash
docker compose down
```
