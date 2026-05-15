from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Goal, User
from app.schemas import GoalCreate, GoalRead, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/", response_model=list[GoalRead])
def list_goals(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Goal]:
    return session.exec(select(Goal).where(Goal.user_id == current_user.id)).all()


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Goal:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.post("/", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Goal:
    if payload.current_amount > payload.target_amount:
        raise HTTPException(status_code=400, detail="current_amount cannot exceed target_amount")
    goal = Goal.model_validate(payload, update={"user_id": current_user.id})
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Goal:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    update_data = payload.model_dump(exclude_unset=True)
    target_amount = update_data.get("target_amount", goal.target_amount)
    current_amount = update_data.get("current_amount", goal.current_amount)
    if current_amount > target_amount:
        raise HTTPException(status_code=400, detail="current_amount cannot exceed target_amount")

    for key, value in update_data.items():
        setattr(goal, key, value)

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    session.delete(goal)
    session.commit()
    return {"ok": True}

