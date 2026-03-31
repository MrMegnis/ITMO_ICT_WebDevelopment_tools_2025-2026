from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.security import hash_password, verify_password
from app.db import get_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import PasswordChange, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
    _: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[User]:
    return session.exec(select(User)).all()


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is invalid")
    if payload.old_password == payload.new_password:
        raise HTTPException(status_code=400, detail="New password must be different")

    current_user.hashed_password = hash_password(payload.new_password)
    session.add(current_user)
    session.commit()
    return {"ok": True}

