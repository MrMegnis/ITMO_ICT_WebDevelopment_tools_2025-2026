from app.celery_app import celery_app
from app.parser import parse_and_save


@celery_app.task(name="parser.parse_url")
def parse_url_task(url: str, user_id: int) -> dict[str, str | int | float | None]:
    return parse_and_save(url, user_id=user_id, source="celery").as_dict()
