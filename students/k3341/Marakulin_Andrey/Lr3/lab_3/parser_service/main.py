from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

from app.parser import parse_and_save_async

app = FastAPI(title="Lab 3 - Parser Service")


class ParseRequest(BaseModel):
    url: HttpUrl
    user_id: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse")
async def parse(payload: ParseRequest) -> dict[str, str | int | float | None]:
    result = await parse_and_save_async(
        str(payload.url),
        user_id=payload.user_id,
        source="parser-service",
    )
    return result.as_dict()
