import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DB_ADMIN",
        "postgresql+psycopg://postgres:postgres@localhost:5432/personal_finance_lab1",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change_this_secret")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()

