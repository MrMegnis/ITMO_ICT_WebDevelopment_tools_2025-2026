from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Tag, TransactionTagLink, User
from app.schemas import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[TagRead])
def list_tags(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Tag]:
    return session.exec(select(Tag).where(Tag.user_id == current_user.id)).all()


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Tag:
    tag = Tag.model_validate(payload, update={"user_id": current_user.id})
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(tag, key, value)

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    is_used = session.exec(select(TransactionTagLink).where(TransactionTagLink.tag_id == tag_id)).first()
    if is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag is used by transactions",
        )

    session.delete(tag)
    session.commit()
    return {"ok": True}
