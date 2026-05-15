from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Budget, Category, Transaction, User
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Category]:
    return session.exec(select(Category).where(Category.user_id == current_user.id)).all()


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Category:
    category = Category.model_validate(payload, update={"user_id": current_user.id})
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    has_transactions = session.exec(
        select(Transaction).where(Transaction.category_id == category_id, Transaction.user_id == current_user.id),
    ).first()
    has_budgets = session.exec(
        select(Budget).where(Budget.category_id == category_id, Budget.user_id == current_user.id),
    ).first()
    if has_transactions or has_budgets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is used by transactions or budgets",
        )

    session.delete(category)
    session.commit()
    return {"ok": True}
