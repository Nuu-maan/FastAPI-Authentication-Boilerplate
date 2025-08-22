from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.security import decode_jwt
from app.models import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(request: Request, db: Session = Depends(get_db_session)):
    access = request.cookies.get("access_token")
    if not access:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_jwt(access)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
        uid = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
