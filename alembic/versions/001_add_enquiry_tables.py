"""add enquiry tables

Revision ID: 001_add_enquiry_tables
Revises:
Create Date: 2026-04-17
"""
from alembic import op
import sqlalchemy as sa


revision = "001_add_enquiry_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enquiries",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("enquiry_number", sa.String(20), unique=True, index=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False, index=True),
        sa.Column("product_service_type", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("pincode", sa.String(6), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "enquiry_vendor_responses",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("enquiry_id", sa.Integer(), sa.ForeignKey("enquiries.id"), nullable=False, index=True),
        sa.Column("vendor_id", sa.Integer(), sa.ForeignKey("vendors.id"), nullable=False, index=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("eta", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="submitted"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "enquiry_messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("response_id", sa.Integer(), sa.ForeignKey("enquiry_vendor_responses.id"), nullable=False, index=True),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sender_role", sa.String(20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("enquiry_messages")
    op.drop_table("enquiry_vendor_responses")
    op.drop_table("enquiries")
