"""add_report_visual_notes

Revision ID: 45c5311424c8
Revises: a5e3aa24e284
Create Date: 2026-06-11 19:17:07.025386
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '45c5311424c8'
down_revision: Union[str, None] = 'a5e3aa24e284'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("report", sa.Column("visual_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("report", "visual_notes")
