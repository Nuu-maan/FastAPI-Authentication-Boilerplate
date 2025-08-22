from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import SessionToken


def list_sessions(db: Session, user_id: int) -> list[SessionToken]:
    stmt = select(SessionToken).where(SessionToken.user_id == user_id).order_by(SessionToken.created_at.desc())
    return list(db.scalars(stmt))


def revoke_session(db: Session, user_id: int, session_id: int) -> bool:
    obj = db.get(SessionToken, session_id)
    if not obj or obj.user_id != user_id:
        return False
    if obj.revoked_at is None:
        obj.revoked_at = datetime.utcnow()
        db.add(obj)
        db.commit()
    return True
