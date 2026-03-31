from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Budget, Category, User
from app.schemas import BudgetCreate, BudgetRead, BudgetUpdate

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _check_category(category_id: int, user_id: int, session: Session) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != user_id:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/", response_model=list[BudgetRead])
def list_budgets(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Budget]:
    return session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Budget:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Budget:
    _check_category(payload.category_id, current_user.id, session)
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")

    budget = Budget.model_validate(payload, update={"user_id": current_user.id})
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Budget:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        _check_category(update_data["category_id"], current_user.id, session)

    start_date = update_data.get("start_date", budget.start_date)
    end_date = update_data.get("end_date", budget.end_date)
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")

    for key, value in update_data.items():
        setattr(budget, key, value)

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    session.delete(budget)
    session.commit()
    return {"ok": True}

