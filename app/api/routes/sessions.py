from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.security import decode_jwt
from app.schemas.session import SessionOut
from app.services.sessions import list_sessions, revoke_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


auth_error = HTTPException(status_code=401, detail="Not authenticated")


def _get_user_id_from_cookie(request: Request) -> int:
    access = request.cookies.get("access_token")
    if not access:
        raise auth_error
    try:
        payload = decode_jwt(access)
        if payload.get("type") != "access":
            raise auth_error
        return int(payload.get("sub"))
    except Exception:
        raise auth_error


@router.get("/", response_model=list[SessionOut])
def get_sessions(request: Request, db: Session = Depends(get_db_session)):
    uid = _get_user_id_from_cookie(request)
    return list_sessions(db, uid)


@router.post("/{session_id}/revoke")
def revoke(session_id: int, request: Request, db: Session = Depends(get_db_session)):
    uid = _get_user_id_from_cookie(request)
    ok = revoke_session(db, uid, session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "revoked"}
