from __future__ import annotations
from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_jwt_token, fingerprint
from app.models import User, SessionToken, EmailToken, Role


ACCESS_TTL = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TTL = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def _random_token(n: int = 48) -> str:
    return secrets.token_urlsafe(n)


def _hash_refresh(raw: str) -> str:
    # simple SHA256 for token reference; not reversible
    import hashlib
    return hashlib.sha256(raw.encode()).hexdigest()


def register(db: Session, email: str, password: str) -> User:
    if db.scalar(select(User).where(User.email == email)):
        raise ValueError("Email already registered")
    user = User(email=email, password_hash=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_session(db: Session, user: User, ip: str, user_agent: str) -> Tuple[str, str, SessionToken]:
    rid = _random_token(32)
    rhash = _hash_refresh(rid)
    fp = fingerprint(ip, user_agent)

    st = SessionToken(
        user_id=user.id,
        refresh_token_hash=rhash,
        ip=ip,
        user_agent=user_agent,
        device_fingerprint=fp,
    )
    db.add(st)
    db.commit()
    db.refresh(st)

    access = create_jwt_token(str(user.id), ACCESS_TTL, "access")
    refresh = create_jwt_token(str(user.id), REFRESH_TTL, "refresh", {"sid": st.id})
    # note: raw rid is not stored; we use JWT as refresh cookie and store hash separately
    return access, refresh, st


def login(db: Session, email: str, password: str, ip: str, user_agent: str) -> Tuple[str, str, SessionToken]:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")
    return create_session(db, user, ip, user_agent)


def rotate_refresh(db: Session, user_id: int, session_id: int, ip: str, user_agent: str) -> Tuple[str, str, SessionToken]:
    st = db.get(SessionToken, session_id)
    if not st or st.user_id != user_id or st.revoked_at is not None:
        raise ValueError("Invalid session")
    # revoke old
    st.revoked_at = datetime.utcnow()
    db.add(st)
    db.commit()
    # create new
    user = db.get(User, user_id)
    return create_session(db, user, ip, user_agent)


def request_email_token(db: Session, user: User, purpose: str, expires_at: datetime) -> EmailToken:
    token = _random_token(32)
    et = EmailToken(user_id=user.id, token=token, purpose=purpose, expires_at=expires_at)
    db.add(et)
    db.commit()
    db.refresh(et)
    return et


def consume_email_token(db: Session, token: str, purpose: str) -> Optional[EmailToken]:
    et = db.scalar(select(EmailToken).where(EmailToken.token == token, EmailToken.purpose == purpose))
    if not et or et.used:
        return None
    if et.expires_at < datetime.utcnow():
        return None
    et.used = True
    db.add(et)
    db.commit()
    db.refresh(et)
    return et
