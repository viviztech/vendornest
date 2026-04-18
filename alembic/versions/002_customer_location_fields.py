"""add city and pincode to customers

Revision ID: 002_customer_location_fields
Revises: 001_add_enquiry_tables
Create Date: 2026-04-17
"""
from alembic import op
import sqlalchemy as sa


revision = "002_customer_location_fields"
down_revision = "001_add_enquiry_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("city", sa.String(200), nullable=True))
    op.add_column("customers", sa.Column("pincode", sa.String(6), nullable=True))


def downgrade() -> None:
    op.drop_column("customers", "pincode")
    op.drop_column("customers", "city")
