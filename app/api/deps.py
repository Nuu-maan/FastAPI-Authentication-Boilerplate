from typing import Generator, Optional
from fastapi import Cookie, Header, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_jwt


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user_id_optional(
    request: Request,
    access_token: Optional[str] = Cookie(default=None, alias="access_token"),
) -> Optional[int]:
    if not access_token:
        return None
    try:
        payload = decode_jwt(access_token)
        if payload.get("type") != "access":
            return None
        sub = payload.get("sub")
        return int(sub)
    except Exception:
        return None


def get_client_meta(ua: Optional[str] = Header(None, alias="User-Agent"), request: Request = None):
    ip = request.client.host if request and request.client else "0.0.0.0"
    return {"ip": ip, "user_agent": ua or ""}
