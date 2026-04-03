# Практика 1.1 (вариант: личные финансы)

Реализовано FastAPI-приложение с:
- временной БД по главной таблице `transactions` (3 записи);
- вложенным одиночным объектом `category`;
- вложенным списком объектов `tags`;
- CRUD API для `transactions`;
- отдельным CRUD API для вложенного объекта `categories`.

## Структура

- `app/models.py` - Pydantic-модели
- `app/main.py` - FastAPI приложение и эндпоинты

## Установка

```bash
pip install fastapi[all]
```

## Запуск

```bash
uvicorn app.main:app --reload
```

## Проверка

- Swagger UI: `http://127.0.0.1:8000/docs`
- Корневой эндпоинт: `GET /`
- Транзакции: `GET/POST /transaction`, `GET/PUT/DELETE /transaction/{transaction_id}`, `GET /transactions`
- Категории: `GET/POST /category`, `GET/PUT/DELETE /category/{category_id}`, `GET /categories`
