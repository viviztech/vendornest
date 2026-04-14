#!/usr/bin/env python3
"""Create superadmin user. Run once after first migration."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.config import settings
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(email=settings.superadmin_email).first()
        if existing:
            print(f"Admin already exists: {settings.superadmin_email}")
            return
        admin = User(
            email=settings.superadmin_email,
            name=settings.superadmin_name,
            hashed_password=pwd_ctx.hash(settings.superadmin_password),
            role=UserRole.superadmin,
            is_active=True,
            is_email_verified=True,
        )
        db.add(admin)
        db.commit()
        print(f"Superadmin created: {settings.superadmin_email}")
        print(f"Password: {settings.superadmin_password}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
