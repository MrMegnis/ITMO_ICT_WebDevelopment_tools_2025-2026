# Лабораторная работа 1. Реализация серверного приложения FastAPI

## Информация о работе

| Параметр | Значение |
|----------|----------|
| Студент | Маракулин Андрей |
| Группа | К3341 |
| Вариант | Разработка сервиса для управления личными финансами |
| Формат | FastAPI + SQLModel + PostgreSQL + Alembic |
| Уровень | Задание на 15 баллов |

## Ссылки на исходный код

- Репозиторий: [ITMO_ICT_WebDevelopment_tools_2025-2026](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026)
- Практика 1.1: [practice_1_1](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Marakulin_Andrey/Lr1/practice_1_1)
- Практика 1.2: [practice_1_2](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Marakulin_Andrey/Lr1/practice_1_2)
- Практика 1.3: [practice_1_3](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Marakulin_Andrey/Lr1/practice_1_3)
- Лабораторная работа: [lab_1](https://github.com/MrMegnis/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3341/Marakulin_Andrey/Lr1/lab_1)

## Цель работы

Разработать полноценное серверное приложение на FastAPI для учета личных финансов с поддержкой:
- хранения данных в PostgreSQL через ORM;
- миграций Alembic;
- CRUD API с вложенными связанными объектами;
- аутентификации и авторизации по JWT;
- пользовательского функционала, необходимого для задания на 15 баллов.

## Выполнение практик 1.1-1.3

### Практика 1.1

Реализовано базовое FastAPI-приложение с временной in-memory БД:
- CRUD для транзакций;
- CRUD для категорий;
- вложенный объект `category` и вложенный список `tags` в модели транзакции;
- Pydantic-валидация.

### Практика 1.2

Проект перенесен на SQLModel и реальную БД:
- модели `Category`, `Tag`, `Transaction`, `TransactionTagLink`;
- связи `one-to-many` и `many-to-many`;
- получение транзакции с вложенными связями;
- полноценные CRUD-методы через `Session`.

### Практика 1.3

Добавлены инфраструктурные требования:
- `.env` и загрузка переменных окружения;
- `.gitignore` для служебных и секретных файлов;
- настройка Alembic;
- миграция `066cf4ac944f_add_level_to_transaction_tag_link.py`, добавляющая поле `level` в ассоциативную таблицу.

## Итоговая лабораторная (15 баллов)

### Структура проекта

```text
lab_1/
  app/
    core/
      config.py
      security.py
    routers/
      auth.py
      users.py
      categories.py
      tags.py
      transactions.py
      budgets.py
      goals.py
      reports.py
    db.py
    dependencies.py
    main.py
    models.py
    schemas.py
  migrations/
    env.py
    versions/0001_initial_personal_finance.py
  docker-compose.yml
  .env
  .env.example
```

### Модели и связи БД

В финальном проекте реализовано 7 таблиц:
- `app_user`
- `category`
- `tag`
- `transaction`
- `transactiontaglink`
- `budget`
- `goal`

Связи:
- `User 1->N Category/Tag/Transaction/Budget/Goal`
- `Category 1->N Transaction`
- `Category 1->N Budget`
- `Transaction N<->N Tag` через `TransactionTagLink`

Ассоциативная сущность `TransactionTagLink` содержит дополнительные поля связи:
- `importance` (1..5)
- `tagged_reason`

Это удовлетворяет требованию примечания по п.3 (ассоциативная сущность с дополнительными атрибутами).

### Подключение к БД

```python
# app/db.py
from sqlmodel import Session, create_engine
from .core.config import settings

engine = create_engine(settings.database_url, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
```

```python
# app/core/config.py
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")
database_url = os.getenv("DB_ADMIN", "postgresql+psycopg://postgres:postgres@localhost:5432/personal_finance_lab1")
```

### Ручная реализация JWT и хэширования (требование 15 баллов)

Реализовано вручную в `app/core/security.py` без библиотек готовой JWT-аутентификации:
- `hash_password` и `verify_password` на `hashlib.pbkdf2_hmac` + `hmac.compare_digest`;
- `create_access_token` и `decode_access_token` с ручной сборкой/проверкой JWT (`header.payload.signature`) через HMAC-SHA256 и base64url.

## Реализованные API-эндпоинты

### Auth
- `POST /auth/register`
- `POST /auth/login`

### Users
- `GET /users/me`
- `GET /users/`
- `POST /users/change-password`

### Categories
- `GET /categories/`
- `GET /categories/{category_id}`
- `POST /categories/`
- `PATCH /categories/{category_id}`
- `DELETE /categories/{category_id}`

### Tags
- `GET /tags/`
- `GET /tags/{tag_id}`
- `POST /tags/`
- `PATCH /tags/{tag_id}`
- `DELETE /tags/{tag_id}`

### Transactions
- `GET /transactions/`
- `GET /transactions/{transaction_id}`
- `POST /transactions/`
- `PATCH /transactions/{transaction_id}`
- `DELETE /transactions/{transaction_id}`

Особенность: возврат вложенных данных по категории и тегам, включая поля связи `importance` и `tagged_reason`.

### Budgets
- `GET /budgets/`
- `GET /budgets/{budget_id}`
- `POST /budgets/`
- `PATCH /budgets/{budget_id}`
- `DELETE /budgets/{budget_id}`

### Goals
- `GET /goals/`
- `GET /goals/{goal_id}`
- `POST /goals/`
- `PATCH /goals/{goal_id}`
- `DELETE /goals/{goal_id}`

### Reports
- `GET /reports/summary`

Возвращает:
- `total_income`
- `total_expense`
- `balance`
- `budgets_exceeded`

## Миграции Alembic

Настроены и применяются миграции:
- `migrations/env.py` использует `SQLModel.metadata` и берет `DB_ADMIN` из `.env`;
- создана первичная миграция `0001_initial_personal_finance.py` со всеми таблицами;
- миграция включает тип `transactiontype` (`income`/`expense`) и внешние ключи.

## Проверка соответствия критериям

### Блок на 9 баллов
- ORM SQLModel + PostgreSQL: выполнено
- CRUD API: выполнено
- GET с вложенными объектами и связями: выполнено
- Alembic: выполнено
- Аннотации типов и схемы: выполнено
- Разделение проекта по слоям/файлам: выполнено

### Дополнительный блок на 15 баллов
- Регистрация и авторизация: выполнено
- Генерация JWT: выполнено
- JWT-аутентификация: выполнено
- Хэширование паролей: выполнено
- Методы `/users/me`, `/users/`, `/users/change-password`: выполнено
- Пункт про ручную реализацию JWT-аутентификации: выполнено

## Запуск проекта

```bash
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger:
- `http://127.0.0.1:8000/docs`

## Вывод

Лабораторная работа выполнена в полном объеме по варианту «Сервис управления личными финансами». Выполнены практики 1.1-1.3 в отдельных папках, реализована финальная версия API с БД, миграциями, связями `one-to-many`/`many-to-many`, ассоциативной сущностью с дополнительными полями и пользовательским функционалом для уровня 15 баллов.

