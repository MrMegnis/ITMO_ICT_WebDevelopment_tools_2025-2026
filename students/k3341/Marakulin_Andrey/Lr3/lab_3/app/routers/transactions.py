from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Category, Tag, Transaction, TransactionTagLink, User
from app.schemas import (
    TransactionCreate,
    TransactionRead,
    TransactionTagRead,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _ensure_category_access(session: Session, category_id: int | None, user_id: int) -> None:
    if category_id is None:
        return
    category = session.get(Category, category_id)
    if not category or category.user_id != user_id:
        raise HTTPException(status_code=404, detail="Category not found")


def _validate_and_get_tags(session: Session, tag_ids: list[int], user_id: int) -> list[Tag]:
    if not tag_ids:
        return []
    if len(tag_ids) != len(set(tag_ids)):
        raise HTTPException(status_code=400, detail="Duplicate tags are not allowed")
    tags = session.exec(select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)).all()
    if len(tags) != len(set(tag_ids)):
        raise HTTPException(status_code=404, detail="One or more tags not found")
    return tags


def _build_transaction_read(session: Session, transaction: Transaction) -> TransactionRead:
    links = session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id == transaction.id),
    ).all()
    link_map = {link.tag_id: link for link in links}

    tags = []
    for tag in transaction.tags:
        link = link_map.get(tag.id)
        tags.append(
            TransactionTagRead(
                id=tag.id,
                name=tag.name,
                importance=link.importance if link else 1,
                tagged_reason=link.tagged_reason if link else "manual",
            ),
        )

    category = None
    if transaction.category:
        category = {
            "id": transaction.category.id,
            "title": transaction.category.title,
            "description": transaction.category.description,
        }

    return TransactionRead(
        id=transaction.id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        note=transaction.note,
        occurred_at=transaction.occurred_at,
        category_id=transaction.category_id,
        category=category,
        tags=tags,
    )


@router.get("/", response_model=list[TransactionRead])
def list_transactions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[TransactionRead]:
    transactions = session.exec(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.category), selectinload(Transaction.tags)),
    ).all()
    return [_build_transaction_read(session, tx) for tx in transactions]


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TransactionRead:
    transaction = session.exec(
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.category), selectinload(Transaction.tags)),
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return _build_transaction_read(session, transaction)


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TransactionRead:
    _ensure_category_access(session, payload.category_id, current_user.id)
    _validate_and_get_tags(session, [item.tag_id for item in payload.tags], current_user.id)

    transaction = Transaction.model_validate(
        payload.model_dump(exclude={"tags"}),
        update={"user_id": current_user.id},
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    for item in payload.tags:
        link = TransactionTagLink(
            transaction_id=transaction.id,
            tag_id=item.tag_id,
            importance=item.importance,
            tagged_reason=item.tagged_reason,
        )
        session.add(link)

    session.commit()
    loaded_transaction = session.exec(
        select(Transaction)
        .where(Transaction.id == transaction.id)
        .options(selectinload(Transaction.category), selectinload(Transaction.tags)),
    ).one()
    return _build_transaction_read(session, loaded_transaction)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TransactionRead:
    transaction = session.exec(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id),
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    update_data = payload.model_dump(exclude_unset=True, exclude={"tags"})
    if "category_id" in update_data:
        _ensure_category_access(session, update_data["category_id"], current_user.id)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    session.add(transaction)
    session.commit()

    if payload.tags is not None:
        _validate_and_get_tags(session, [item.tag_id for item in payload.tags], current_user.id)
        session.exec(
            delete(TransactionTagLink).where(TransactionTagLink.transaction_id == transaction.id),
        )
        for item in payload.tags:
            session.add(
                TransactionTagLink(
                    transaction_id=transaction.id,
                    tag_id=item.tag_id,
                    importance=item.importance,
                    tagged_reason=item.tagged_reason,
                ),
            )
        session.commit()

    loaded_transaction = session.exec(
        select(Transaction)
        .where(Transaction.id == transaction.id)
        .options(selectinload(Transaction.category), selectinload(Transaction.tags)),
    ).one()
    return _build_transaction_read(session, loaded_transaction)


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    transaction = session.exec(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id),
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    session.exec(delete(TransactionTagLink).where(TransactionTagLink.transaction_id == transaction.id))
    session.delete(transaction)
    session.commit()
    return {"ok": True}
