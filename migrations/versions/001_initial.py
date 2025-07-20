"""Initial migration: users and clicks tables

Revision ID: 001_initial
Revises:
Create Date: 2026-03-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "clicks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("short_code", sa.String(20), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("clicked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clicks_short_code"), "clicks", ["short_code"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_clicks_short_code"), table_name="clicks")
    op.drop_table("clicks")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
