from sqlalchemy.orm import Session

from app.models import AuditLog


def log_action(
    db: Session, *, user_id: int | None, action: str, ip: str, user_agent: str
) -> None:
    entry = AuditLog(user_id=user_id, action=action, ip=ip, user_agent=user_agent)
    db.add(entry)
    db.commit()
