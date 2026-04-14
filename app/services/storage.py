"""AWS S3 file upload/delete service."""
import boto3
import uuid
import os
from typing import Optional
from fastapi import UploadFile
import logging

from app.config import settings

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_DOC_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB
MAX_DOC_SIZE = 10 * 1024 * 1024    # 10 MB


def _s3():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def upload_file(
    file: UploadFile,
    folder: str,
    allowed_types: set = ALLOWED_IMAGE_TYPES,
    max_size: int = MAX_IMAGE_SIZE,
) -> Optional[str]:
    """Upload file to S3 and return public URL."""
    if file.content_type not in allowed_types:
        raise ValueError(f"File type {file.content_type} not allowed")

    contents = file.file.read()
    if len(contents) > max_size:
        raise ValueError(f"File too large. Max {max_size // (1024*1024)}MB allowed")

    ext = os.path.splitext(file.filename or "file")[1] or ".jpg"
    key = f"{folder}/{uuid.uuid4().hex}{ext}"

    try:
        _s3().put_object(
            Bucket=settings.aws_s3_bucket,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
        return f"{settings.media_base_url}/{key}"
    except Exception as e:
        logger.error(f"S3 upload error: {e}")
        return None


def delete_file(url: str) -> bool:
    """Delete file from S3 by URL."""
    try:
        key = url.split(settings.aws_s3_bucket + "/")[-1]
        _s3().delete_object(Bucket=settings.aws_s3_bucket, Key=key)
        return True
    except Exception as e:
        logger.error(f"S3 delete error: {e}")
        return False


def upload_product_image(file: UploadFile) -> Optional[str]:
    return upload_file(file, "products", ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)


def upload_vendor_doc(file: UploadFile) -> Optional[str]:
    return upload_file(file, "vendor-docs", ALLOWED_DOC_TYPES, MAX_DOC_SIZE)


def upload_brand_logo(file: UploadFile) -> Optional[str]:
    return upload_file(file, "brands", ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)


def upload_invoice(content: bytes, filename: str) -> Optional[str]:
    key = f"invoices/{filename}"
    try:
        _s3().put_object(
            Bucket=settings.aws_s3_bucket,
            Key=key,
            Body=content,
            ContentType="application/pdf",
        )
        return f"{settings.media_base_url}/{key}"
    except Exception as e:
        logger.error(f"S3 invoice upload error: {e}")
        return None
