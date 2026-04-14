"""Celery tasks: send queued notifications."""
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.notification import NotificationLog, NotificationStatus
from app.services.notification import send_email
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="send_pending_emails")
def send_pending_emails():
    db = SessionLocal()
    try:
        pending = db.query(NotificationLog).filter_by(
            type="email", status=NotificationStatus.pending
        ).limit(50).all()
        for log in pending:
            success = send_email(log.recipient, log.subject or "", log.body or "")
            log.status = NotificationStatus.sent if success else NotificationStatus.failed
        db.commit()
    finally:
        db.close()
