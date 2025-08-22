from typing import Optional

from fastapi import Response

from app.core.config import settings


def set_cookie(
    response: Response, name: str, value: str, max_age: Optional[int] = None
) -> None:
    response.set_cookie(
        key=name,
        value=value,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=max_age,
        path="/",
    )


def clear_cookie(response: Response, name: str) -> None:
    response.delete_cookie(key=name, path="/")
