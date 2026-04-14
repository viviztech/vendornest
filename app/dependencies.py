"""FastAPI dependencies: auth guards, DB session, pagination."""
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth import decode_token, get_user_by_id


class LoginRequired(Exception):
    pass


def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = get_token_from_cookie(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_user_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


def _resolve_user(request: Request, db: Session) -> Optional[User]:
    token = get_token_from_cookie(request)
    if not token:
        return None
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user = get_user_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        return None
    return user


def require_superadmin(request: Request, db: Session = Depends(get_db)):
    user = _resolve_user(request, db)
    if not user:
        raise LoginRequired()
    if user.role != UserRole.superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def require_vendor(request: Request, db: Session = Depends(get_db)):
    user = _resolve_user(request, db)
    if not user:
        raise LoginRequired()
    if user.role != UserRole.vendor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor access required")
    return user


def require_customer(request: Request, db: Session = Depends(get_db)):
    user = _resolve_user(request, db)
    if not user:
        raise LoginRequired()
    if user.role != UserRole.customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required")
    return user


def require_admin_or_vendor(request: Request, db: Session = Depends(get_db)):
    user = _resolve_user(request, db)
    if not user:
        raise LoginRequired()
    if user.role not in (UserRole.superadmin, UserRole.vendor):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return user


class Pagination:
    def __init__(self, page: int = 1, size: int = 20):
        self.page = max(1, page)
        self.size = min(size, 100)
        self.offset = (self.page - 1) * self.size
