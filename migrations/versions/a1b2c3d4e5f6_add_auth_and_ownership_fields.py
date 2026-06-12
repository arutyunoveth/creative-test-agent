"""add_auth_and_ownership_fields

Revision ID: a1b2c3d4e5f6
Revises: fc9b3a7e2d51
Create Date: 2026-06-11 21:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fc9b3a7e2d51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("client", sa.Column("created_by_user_id", sa.String(255), nullable=True))
    op.add_column("client", sa.Column("updated_by_user_id", sa.String(255), nullable=True))
    op.add_column("project", sa.Column("created_by_user_id", sa.String(255), nullable=True))
    op.add_column("project", sa.Column("updated_by_user_id", sa.String(255), nullable=True))
    op.add_column("creative_asset", sa.Column("created_by_user_id", sa.String(255), nullable=True))
    op.add_column("creative_asset", sa.Column("updated_by_user_id", sa.String(255), nullable=True))
    op.add_column("test_run", sa.Column("created_by_user_id", sa.String(255), nullable=True))
    op.add_column("test_run", sa.Column("updated_by_user_id", sa.String(255), nullable=True))
    op.add_column("report", sa.Column("created_by_user_id", sa.String(255), nullable=True))
    op.add_column("report", sa.Column("updated_by_user_id", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("report", "created_by_user_id")
    op.drop_column("report", "updated_by_user_id")
    op.drop_column("test_run", "created_by_user_id")
    op.drop_column("test_run", "updated_by_user_id")
    op.drop_column("creative_asset", "created_by_user_id")
    op.drop_column("creative_asset", "updated_by_user_id")
    op.drop_column("project", "created_by_user_id")
    op.drop_column("project", "updated_by_user_id")
    op.drop_column("client", "created_by_user_id")
    op.drop_column("client", "updated_by_user_id")
