from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db_session, get_client_meta
from app.core.config import settings
from app.core.rate_limit import is_allowed
from app.core.security import decode_jwt
from app.core.security import get_password_hash
from app.schemas.auth import LoginIn, PasswordResetRequestIn, PasswordResetIn
from app.schemas.user import UserCreate, UserOut
from app.schemas.common import MessageOut
from app.services import auth as auth_svc
from app.services.email import get_email_service
from app.services.audit import log_action
from app.utils.cookies import set_cookie, clear_cookie
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db_session),
    meta: dict = Depends(get_client_meta),
    request: Request = None,
):
    try:
        user = auth_svc.register(db, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # send email verification (stub)
    et = auth_svc.request_email_token(
        db,
        user,
        purpose="verify_email",
        expires_at=datetime.utcnow() + timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS),
    )
    get_email_service().send_verification(user.email, et.token)

    log_action(db, user_id=user.id, action="register", ip=meta["ip"], user_agent=meta["user_agent"])  # type: ignore[index]
    return user


@router.post("/login", response_model=MessageOut)
def login(
    payload: LoginIn,
    response: Response,
    db: Session = Depends(get_db_session),
    meta: dict = Depends(get_client_meta),
    request: Request = None,
):
    rl_key = f"login:{payload.email}:{meta['ip']}"
    allowed, retry_after = is_allowed(rl_key, limit=5, window_seconds=60)
    if not allowed:
        raise HTTPException(status_code=429, detail=f"Too many attempts. Try again in {retry_after}s")

    try:
        access, refresh, st = auth_svc.login(db, payload.email, payload.password, meta["ip"], meta["user_agent"])  # type: ignore[index]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    set_cookie(response, "access_token", access, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    set_cookie(response, "refresh_token", refresh, max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)

    log_action(db, user_id=st.user_id, action="login", ip=meta["ip"], user_agent=meta["user_agent"])  # type: ignore[index]
    return {"message": "logged in"}


@router.post("/logout", response_model=MessageOut)
def logout(
    response: Response,
    db: Session = Depends(get_db_session),
    meta: dict = Depends(get_client_meta),
    request: Request = None,
):
    # best-effort: revoke by refresh sid in cookie
    clear_cookie(response, "access_token")
    clear_cookie(response, "refresh_token")
    log_action(db, user_id=None, action="logout", ip=meta["ip"], user_agent=meta["user_agent"])  # type: ignore[index]
    return {"message": "logged out"}


@router.post("/refresh", response_model=MessageOut)
def refresh(
    response: Response,
    request: Request,
    db: Session = Depends(get_db_session),
    meta: dict = Depends(get_client_meta),
):
    refresh_cookie = request.cookies.get("refresh_token")
    if not refresh_cookie:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        payload = decode_jwt(refresh_cookie)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        uid = int(payload.get("sub"))
        sid = int(payload.get("sid"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        access, new_refresh, st = auth_svc.rotate_refresh(db, uid, sid, meta["ip"], meta["user_agent"])  # type: ignore[index]
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    set_cookie(response, "access_token", access, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    set_cookie(response, "refresh_token", new_refresh, max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)

    log_action(db, user_id=uid, action="refresh", ip=meta["ip"], user_agent=meta["user_agent"])  # type: ignore[index]
    return {"message": "refreshed"}


@router.post("/resend-verification", response_model=MessageOut)
def resend_verification(request: Request, db: Session = Depends(get_db_session)):
    # optional: only for logged-in users, but here we accept email via cookie if access presents
    access = request.cookies.get("access_token")
    if not access:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_jwt(access)
        uid = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user: User | None = db.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    et = auth_svc.request_email_token(
        db,
        user,
        purpose="verify_email",
        expires_at=datetime.utcnow() + timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS),
    )
    get_email_service().send_verification(user.email, et.token)
    return {"message": "verification sent"}


@router.get("/verify-email", response_model=MessageOut)
def verify_email(
    token: str,
    db: Session = Depends(get_db_session),
    meta: dict = Depends(get_client_meta),
    request: Request = None,
):
    et = auth_svc.consume_email_token(db, token, purpose="verify_email")
    if not et:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.get(User, et.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_email_verified = True
    db.add(user)
    db.commit()

    log_action(db, user_id=user.id, action="verify", ip=meta["ip"], user_agent=meta["user_agent"])  # type: ignore[index]
    return {"message": "email verified"}


@router.post("/request-password-reset", response_model=MessageOut)
def request_password_reset(payload: PasswordResetRequestIn, db: Session = Depends(get_db_session)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if user:
        et = auth_svc.request_email_token(
            db,
            user,
            purpose="reset_password",
            expires_at=datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS),
        )
        get_email_service().send_password_reset(user.email, et.token)
    return {"message": "if account exists, reset email sent"}


@router.post("/reset-password", response_model=MessageOut)
def reset_password(payload: PasswordResetIn, db: Session = Depends(get_db_session)):
    et = auth_svc.consume_email_token(db, payload.token, purpose="reset_password")
    if not et:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.get(User, et.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = get_password_hash(payload.new_password)
    db.add(user)
    db.commit()
    return {"message": "password reset"}
