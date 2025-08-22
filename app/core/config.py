from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = Field(default="fastapi-auth")
    APP_ENV: str = Field(default="dev")

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = Field(default="lax")  # lax, strict, none

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Database selection
    DB_BACKEND: Literal["postgres", "sqlite"] = Field(default="postgres")
    DATABASE_URL: Optional[str] = None  # If provided, overrides DB_BACKEND/SQLITE_PATH
    SQLITE_PATH: str = Field(
        default="./app.db"
    )  # Used when DB_BACKEND=sqlite and DATABASE_URL not provided

    # Redis is optional; if unset, in-memory fallback will be used for simple rate limiting
    REDIS_URL: Optional[str] = None

    EMAIL_FROM: str = "no-reply@example.com"
    EMAIL_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 2

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


settings = get_settings()
