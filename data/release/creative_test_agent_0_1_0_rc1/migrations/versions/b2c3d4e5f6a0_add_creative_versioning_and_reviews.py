"""add_creative_versioning_and_reviews

Revision ID: b2c3d4e5f6a0
Revises: a1b2c3d4e5f6
Create Date: 2026-06-12 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a0'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Versioning columns on creative_asset ──────────────────────────
    op.add_column("creative_asset", sa.Column("parent_asset_id", sa.String(), nullable=True))
    op.add_column("creative_asset", sa.Column("version_label", sa.String(100), nullable=True))
    op.add_column("creative_asset", sa.Column("version_number", sa.Integer(), nullable=True))
    op.add_column("creative_asset", sa.Column("revision_summary", sa.Text(), nullable=True))
    op.add_column("creative_asset", sa.Column("revision_source", sa.String(50), nullable=True))
    op.create_index("ix_creative_asset_parent_asset_id", "creative_asset", ["parent_asset_id"])

    # ── creative_review table ─────────────────────────────────────────
    op.create_table(
        "creative_review",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("creative_asset_id", sa.String(255), nullable=False),
        sa.Column("report_id", sa.String(255), nullable=True),
        sa.Column("project_id", sa.String(255), nullable=True),
        sa.Column("reviewer", sa.String(255), nullable=False),
        sa.Column("reviewer_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("decision", sa.String(50), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("strengths", sa.Text(), nullable=True),
        sa.Column("concerns", sa.Text(), nullable=True),
        sa.Column("revision_requests", sa.Text(), nullable=True),
        sa.Column("feedback_details_json", sa.Text(), nullable=True),
        sa.Column("requested_changes_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creative_review_creative_asset_id", "creative_review", ["creative_asset_id"])
    op.create_index("ix_creative_review_project_id", "creative_review", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_creative_review_project_id", table_name="creative_review")
    op.drop_index("ix_creative_review_creative_asset_id", table_name="creative_review")
    op.drop_table("creative_review")
    op.drop_index("ix_creative_asset_parent_asset_id", table_name="creative_asset")
    op.drop_column("creative_asset", "revision_source")
    op.drop_column("creative_asset", "revision_summary")
    op.drop_column("creative_asset", "version_number")
    op.drop_column("creative_asset", "version_label")
    op.drop_column("creative_asset", "parent_asset_id")
