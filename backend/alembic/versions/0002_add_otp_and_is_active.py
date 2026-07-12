"""add otp table and is_active to users

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False))

    op.create_table(
        "otps",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=6), nullable=False),
        sa.Column("is_used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_otps_id"), "otps", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_otps_id"), table_name="otps")
    op.drop_table("otps")
    op.drop_column("users", "is_active")
