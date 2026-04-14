"""Razorpay payment service."""
import razorpay
import hmac
import hashlib
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def _client():
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def create_order(amount_rupees: float, order_number: str, customer_email: str) -> Optional[dict]:
    """Create Razorpay order. Amount in rupees, converted to paise."""
    try:
        order = _client().order.create({
            "amount": int(amount_rupees * 100),
            "currency": "INR",
            "receipt": order_number,
            "notes": {"customer_email": customer_email, "platform": "VendorNest"},
        })
        return order
    except Exception as e:
        logger.error(f"Razorpay create_order error: {e}")
        return None


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> bool:
    try:
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected = hmac.new(
            settings.razorpay_key_secret.encode(),
            msg.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, razorpay_signature)
    except Exception as e:
        logger.error(f"Signature verify error: {e}")
        return False


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    try:
        expected = hmac.new(
            settings.razorpay_webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


def initiate_refund(payment_id: str, amount_rupees: Optional[float] = None) -> Optional[dict]:
    try:
        params = {}
        if amount_rupees:
            params["amount"] = int(amount_rupees * 100)
        return _client().payment.refund(payment_id, params)
    except Exception as e:
        logger.error(f"Razorpay refund error: {e}")
        return None


def fetch_payment(payment_id: str) -> Optional[dict]:
    try:
        return _client().payment.fetch(payment_id)
    except Exception as e:
        logger.error(f"Razorpay fetch_payment error: {e}")
        return None
