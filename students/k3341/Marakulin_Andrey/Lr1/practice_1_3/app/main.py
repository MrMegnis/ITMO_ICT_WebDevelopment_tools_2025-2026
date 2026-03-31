from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select
from typing_extensions import TypedDict

from .connection import get_session, init_db
from .models import (
    Category,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    Tag,
    TagCreate,
    TagRead,
    TagUpdate,
    Transaction,
    TransactionCreate,
    TransactionRead,
    TransactionReadWithRelations,
    TransactionUpdate,
)

app = FastAPI(title="Practice 1.3 - Personal Finance API with migrations")


class CategoryResponse(TypedDict):
    status: int
    data: CategoryRead


class TagResponse(TypedDict):
    status: int
    data: TagRead


class TransactionResponse(TypedDict):
    status: int
    data: TransactionReadWithRelations


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root() -> str:
    return "Practice 1.3 is running"


@app.get("/categories", response_model=list[CategoryRead])
def categories_list(session: Session = Depends(get_session)) -> list[Category]:
    return session.exec(select(Category)).all()


@app.get("/category/{category_id}", response_model=CategoryRead)
def category_get(category_id: int, session: Session = Depends(get_session)) -> Category:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.post("/category", response_model=CategoryResponse)
def category_create(category: CategoryCreate, session: Session = Depends(get_session)) -> CategoryResponse:
    db_category = Category.model_validate(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return {"status": 200, "data": db_category}


@app.patch("/category/{category_id}", response_model=CategoryRead)
def category_update(
    category_id: int,
    category: CategoryUpdate,
    session: Session = Depends(get_session),
) -> Category:
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = category.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)

    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.delete("/category/{category_id}")
def category_delete(category_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"ok": True}


@app.get("/tags", response_model=list[TagRead])
def tags_list(session: Session = Depends(get_session)) -> list[Tag]:
    return session.exec(select(Tag)).all()


@app.get("/tag/{tag_id}", response_model=TagRead)
def tag_get(tag_id: int, session: Session = Depends(get_session)) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.post("/tag", response_model=TagResponse)
def tag_create(tag: TagCreate, session: Session = Depends(get_session)) -> TagResponse:
    db_tag = Tag.model_validate(tag)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return {"status": 200, "data": db_tag}


@app.patch("/tag/{tag_id}", response_model=TagRead)
def tag_update(tag_id: int, tag: TagUpdate, session: Session = Depends(get_session)) -> Tag:
    db_tag = session.get(Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag_data = tag.model_dump(exclude_unset=True)
    for key, value in tag_data.items():
        setattr(db_tag, key, value)

    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@app.delete("/tag/{tag_id}")
def tag_delete(tag_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()
    return {"ok": True}


@app.get("/transactions", response_model=list[TransactionRead])
def transactions_list(session: Session = Depends(get_session)) -> list[Transaction]:
    return session.exec(select(Transaction)).all()


@app.get("/transaction/{transaction_id}", response_model=TransactionReadWithRelations)
def transaction_get(transaction_id: int, session: Session = Depends(get_session)) -> Transaction:
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/transaction", response_model=TransactionResponse)
def transaction_create(
    transaction: TransactionCreate,
    session: Session = Depends(get_session),
) -> TransactionResponse:
    if transaction.category_id is not None and not session.get(Category, transaction.category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    transaction_data = transaction.model_dump(exclude={"tag_ids"})
    db_transaction = Transaction.model_validate(transaction_data)

    if transaction.tag_ids:
        tags = session.exec(select(Tag).where(Tag.id.in_(transaction.tag_ids))).all()
        if len(tags) != len(set(transaction.tag_ids)):
            raise HTTPException(status_code=404, detail="One or more tags were not found")
        db_transaction.tags = tags

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return {"status": 200, "data": db_transaction}


@app.patch("/transaction/{transaction_id}", response_model=TransactionReadWithRelations)
def transaction_update(
    transaction_id: int,
    transaction: TransactionUpdate,
    session: Session = Depends(get_session),
) -> Transaction:
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction_data = transaction.model_dump(exclude_unset=True)

    if "category_id" in transaction_data and transaction_data["category_id"] is not None:
        if not session.get(Category, transaction_data["category_id"]):
            raise HTTPException(status_code=404, detail="Category not found")

    tag_ids = transaction_data.pop("tag_ids", None)

    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)

    if tag_ids is not None:
        tags = session.exec(select(Tag).where(Tag.id.in_(tag_ids))).all() if tag_ids else []
        if len(tags) != len(set(tag_ids)):
            raise HTTPException(status_code=404, detail="One or more tags were not found")
        db_transaction.tags = tags

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@app.delete("/transaction/{transaction_id}")
def transaction_delete(transaction_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(transaction)
    session.commit()
    return {"ok": True}
