from typing import Any

import httpx
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlmodel import Session, select

from app.celery_app import celery_app
from app.core.config import settings
from app.db import get_session
from app.dependencies import get_current_user
from app.models import ParsedSource, User
from app.schemas import ParsedSourceRead
from app.tasks import parse_url_task

router = APIRouter(prefix="/parser", tags=["parser"])


class ParseRequest(BaseModel):
    url: HttpUrl


@router.get("/sources", response_model=list[ParsedSourceRead])
def list_sources(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[ParsedSource]:
    return session.exec(
        select(ParsedSource)
        .where(ParsedSource.user_id == current_user.id)
        .order_by(ParsedSource.created_at.desc()),
    ).all()


@router.post("/sync")
def parse_sync(
    payload: ParseRequest,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    parser_url = f"{settings.parser_service_url.rstrip('/')}/parse"
    try:
        response = httpx.post(
            parser_url,
            json={"url": str(payload.url), "user_id": current_user.id},
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Parser service is unavailable: {exc}",
        ) from exc
    return response.json()


@router.post("/queue", status_code=status.HTTP_202_ACCEPTED)
def parse_queue(
    payload: ParseRequest,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    task = parse_url_task.delay(str(payload.url), current_user.id)
    return {"task_id": task.id, "status": "queued"}


@router.get("/tasks/{task_id}")
def task_status(
    task_id: str,
    _: User = Depends(get_current_user),
) -> dict[str, Any]:
    task = AsyncResult(task_id, app=celery_app)
    response: dict[str, Any] = {"task_id": task_id, "status": task.status}
    if task.successful():
        response["result"] = task.result
    elif task.failed():
        response["error"] = str(task.result)
    return response
