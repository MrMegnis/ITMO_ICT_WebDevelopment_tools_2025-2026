from typing import List

from fastapi import FastAPI, HTTPException
from typing_extensions import TypedDict

from .models import Category, Transaction

app = FastAPI(title="Practice 1.1 - Personal Finance API")


categories_db: List[dict] = [
    {"id": 1, "title": "Зарплата", "description": "Регулярный доход"},
    {"id": 2, "title": "Продукты", "description": "Покупки еды"},
    {"id": 3, "title": "Транспорт", "description": "Поездки и топливо"},
]

transactions_db: List[dict] = [
    {
        "id": 1,
        "amount": 120000,
        "transaction_type": "income",
        "note": "Зарплата за март",
        "category": categories_db[0],
        "tags": [{"id": 1, "name": "работа"}, {"id": 2, "name": "месяц"}],
    },
    {
        "id": 2,
        "amount": 3400,
        "transaction_type": "expense",
        "note": "Пятерочка",
        "category": categories_db[1],
        "tags": [{"id": 3, "name": "еда"}],
    },
    {
        "id": 3,
        "amount": 1800,
        "transaction_type": "expense",
        "note": "Метро и автобус",
        "category": categories_db[2],
        "tags": [{"id": 4, "name": "дорога"}],
    },
]


class CreateTransactionResponse(TypedDict):
    status: int
    data: Transaction


class CreateCategoryResponse(TypedDict):
    status: int
    data: Category


@app.get("/")
def root() -> str:
    return "Hello, Marakulin Andrey! Practice 1.1 is running."


@app.get("/transactions", response_model=List[Transaction])
def transactions_list() -> List[dict]:
    return transactions_db


@app.get("/transaction/{transaction_id}", response_model=Transaction)
def transaction_get(transaction_id: int) -> dict:
    for transaction in transactions_db:
        if transaction["id"] == transaction_id:
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.post("/transaction")
def transaction_create(transaction: Transaction) -> CreateTransactionResponse:
    if any(item["id"] == transaction.id for item in transactions_db):
        raise HTTPException(status_code=400, detail="Transaction with this id already exists")

    transaction_to_append = transaction.model_dump()
    transactions_db.append(transaction_to_append)
    return {"status": 200, "data": transaction}


@app.delete("/transaction/{transaction_id}")
def transaction_delete(transaction_id: int) -> dict:
    for i, transaction in enumerate(transactions_db):
        if transaction["id"] == transaction_id:
            transactions_db.pop(i)
            return {"status": 200, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.put("/transaction/{transaction_id}", response_model=Transaction)
def transaction_update(transaction_id: int, transaction: Transaction) -> dict:
    for i, current in enumerate(transactions_db):
        if current["id"] == transaction_id:
            updated = transaction.model_dump()
            updated["id"] = transaction_id
            transactions_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.get("/categories", response_model=List[Category])
def categories_list() -> List[dict]:
    return categories_db


@app.get("/category/{category_id}", response_model=Category)
def category_get(category_id: int) -> dict:
    for category in categories_db:
        if category["id"] == category_id:
            return category
    raise HTTPException(status_code=404, detail="Category not found")


@app.post("/category")
def category_create(category: Category) -> CreateCategoryResponse:
    if any(item["id"] == category.id for item in categories_db):
        raise HTTPException(status_code=400, detail="Category with this id already exists")

    category_to_append = category.model_dump()
    categories_db.append(category_to_append)
    return {"status": 200, "data": category}


@app.put("/category/{category_id}", response_model=Category)
def category_update(category_id: int, category: Category) -> dict:
    for i, current in enumerate(categories_db):
        if current["id"] == category_id:
            updated = category.model_dump()
            updated["id"] = category_id
            categories_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Category not found")


@app.delete("/category/{category_id}")
def category_delete(category_id: int) -> dict:
    for i, category in enumerate(categories_db):
        if category["id"] == category_id:
            categories_db.pop(i)
            return {"status": 200, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Category not found")
