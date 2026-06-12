"""add_job_queue_and_batch_tables

Revision ID: c3d4e5f6a0b1
Revises: b2c3d4e5f6a0
Create Date: 2026-06-12 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a0b1'
down_revision: Union[str, None] = 'b2c3d4e5f6a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── job table ─────────────────────────────────────────────────────
    op.create_table(
        "job",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="queued"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.String(255), nullable=True),
        sa.Column("project_id", sa.String(255), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("result_json", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_status", "job", ["status"])
    op.create_index("ix_job_job_type", "job", ["job_type"])

    # ── batch_run table ───────────────────────────────────────────────
    op.create_table(
        "batch_run",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("creative_asset_ids_json", sa.Text(), nullable=True),
        sa.Column("audience_profile_ids_json", sa.Text(), nullable=True),
        sa.Column("brand_profile_id", sa.String(255), nullable=True),
        sa.Column("test_rubric_id", sa.String(255), nullable=True),
        sa.Column("input_context_json", sa.Text(), nullable=True),
        sa.Column("result_summary_json", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_batch_run_project_id", "batch_run", ["project_id"])
    op.create_index("ix_batch_run_status", "batch_run", ["status"])

    # ── batch_run_item table ──────────────────────────────────────────
    op.create_table(
        "batch_run_item",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("batch_run_id", sa.String(255), nullable=False),
        sa.Column("creative_asset_id", sa.String(255), nullable=False),
        sa.Column("audience_profile_id", sa.String(255), nullable=True),
        sa.Column("test_run_id", sa.String(255), nullable=True),
        sa.Column("report_id", sa.String(255), nullable=True),
        sa.Column("job_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("score_summary_json", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_batch_run_item_batch_run_id", "batch_run_item", ["batch_run_id"])
    op.create_index("ix_batch_run_item_status", "batch_run_item", ["status"])


def downgrade() -> None:
    op.drop_index("ix_batch_run_item_status", table_name="batch_run_item")
    op.drop_index("ix_batch_run_item_batch_run_id", table_name="batch_run_item")
    op.drop_table("batch_run_item")
    op.drop_index("ix_batch_run_status", table_name="batch_run")
    op.drop_index("ix_batch_run_project_id", table_name="batch_run")
    op.drop_table("batch_run")
    op.drop_index("ix_job_job_type", table_name="job")
    op.drop_index("ix_job_status", table_name="job")
    op.drop_table("job")
