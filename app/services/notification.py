"""
Notification service: Email via AWS SES.
SMS and WhatsApp stubbed for future activation.
"""
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from jinja2 import Template
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def _ses_client():
    return boto3.client(
        "ses",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def send_email(
    to: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    try:
        client = _ses_client()
        client.send_email(
            Source=f"{settings.ses_from_name} <{settings.ses_from_email}>",
            Destination={"ToAddresses": [to]},
            ReplyToAddresses=[settings.ses_reply_to],
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                    **({"Text": {"Data": text_body, "Charset": "UTF-8"}} if text_body else {}),
                },
            },
        )
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except (BotoCoreError, ClientError) as e:
        logger.error(f"SES error sending to {to}: {e}")
        return False


def send_otp_email(to: str, otp: str, name: str = "") -> bool:
    subject = f"Your VendorNest OTP: {otp}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
      <h2 style="color:#1d4ed8;">VendorNest</h2>
      <p>Hello {name or "there"},</p>
      <p>Your one-time password (OTP) is:</p>
      <div style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#1d4ed8;padding:16px;background:#eff6ff;border-radius:6px;text-align:center;">{otp}</div>
      <p style="color:#6b7280;margin-top:16px;">This OTP is valid for {settings.otp_expire_minutes} minutes. Do not share it with anyone.</p>
      <p style="color:#6b7280;font-size:12px;">If you did not request this, please ignore this email.</p>
    </div>
    """
    return send_email(to, subject, html)


def send_order_confirmation_email(to: str, name: str, order_number: str, total: float) -> bool:
    subject = f"Order Confirmed - #{order_number}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
      <h2 style="color:#1d4ed8;">Order Confirmed!</h2>
      <p>Hello {name},</p>
      <p>Your order <strong>#{order_number}</strong> has been confirmed.</p>
      <p>Total Amount: <strong>₹{total:,.2f}</strong></p>
      <p>You will receive updates as your order is processed and shipped.</p>
      <a href="{settings.app_base_url}/customer/orders/{order_number}"
         style="display:inline-block;padding:12px 24px;background:#1d4ed8;color:white;border-radius:6px;text-decoration:none;">
        Track Order
      </a>
    </div>
    """
    return send_email(to, subject, html)


def send_vendor_approval_email(to: str, name: str, approved: bool, reason: str = "") -> bool:
    if approved:
        subject = "Your VendorNest vendor account is approved!"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
          <h2 style="color:#16a34a;">Congratulations, {name}!</h2>
          <p>Your vendor account on <strong>VendorNest</strong> has been approved.</p>
          <p>You can now log in and start listing your products and services.</p>
          <a href="{settings.app_base_url}/vendor/dashboard"
             style="display:inline-block;padding:12px 24px;background:#16a34a;color:white;border-radius:6px;text-decoration:none;">
            Go to Dashboard
          </a>
        </div>
        """
    else:
        subject = "VendorNest vendor application update"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
          <h2 style="color:#dc2626;">Application Update</h2>
          <p>Hello {name},</p>
          <p>We were unable to approve your vendor application at this time.</p>
          {"<p><strong>Reason:</strong> " + reason + "</p>" if reason else ""}
          <p>Please contact support if you have questions.</p>
        </div>
        """
    return send_email(to, subject, html)


def send_service_booking_email(to: str, name: str, request_number: str, date: str, time_slot: str) -> bool:
    subject = f"Service Request Confirmed - #{request_number}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
      <h2 style="color:#1d4ed8;">Service Request Confirmed</h2>
      <p>Hello {name},</p>
      <p>Your service request <strong>#{request_number}</strong> has been received.</p>
      <p>Preferred Date: <strong>{date}</strong><br>Time Slot: <strong>{time_slot}</strong></p>
      <p>A technician will visit your location. You'll be notified once confirmed.</p>
      <a href="{settings.app_base_url}/customer/services/{request_number}"
         style="display:inline-block;padding:12px 24px;background:#1d4ed8;color:white;border-radius:6px;text-decoration:none;">
        View Status
      </a>
    </div>
    """
    return send_email(to, subject, html)


# ── Stubs for future SMS / WhatsApp ───────────────────────────────────────────
def send_sms(phone: str, message: str) -> bool:
    logger.info(f"[SMS STUB] To {phone}: {message}")
    return True  # Replace with MSG91 when activated


def send_whatsapp(phone: str, template: str, params: dict) -> bool:
    if not settings.whatsapp_enabled:
        logger.info(f"[WhatsApp STUB] To {phone}: {template}")
        return True
    # Meta Cloud API call here when enabled
    return True
