"""add_platform_foundation_tables

Revision ID: fc9b3a7e2d51
Revises: 45c5311424c8
Create Date: 2026-06-11 20:38:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'fc9b3a7e2d51'
down_revision: Union[str, None] = '45c5311424c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── User table ───────────────────────────────────────────────────
    op.create_table(
        "user",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # ── Client table ─────────────────────────────────────────────────
    op.create_table(
        "client",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── Project table ────────────────────────────────────────────────
    op.create_table(
        "project",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── BrandbookDocument table ──────────────────────────────────────
    op.create_table(
        "brandbook_document",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(255), nullable=True),
        sa.Column("project_id", sa.String(255), nullable=True),
        sa.Column("brand_profile_id", sa.String(255), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False, server_default="other"),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("text_content", sa.Text(), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── KnowledgeItem table ──────────────────────────────────────────
    op.create_table(
        "knowledge_item",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="other"),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("client_id", sa.String(255), nullable=True),
        sa.Column("project_id", sa.String(255), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tags_json", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── ExportJob table ──────────────────────────────────────────────
    op.create_table(
        "export_job",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(255), nullable=False),
        sa.Column("export_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="created"),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── Add project_id columns to existing tables ────────────────────
    op.add_column("creative_asset", sa.Column("project_id", sa.String(255), nullable=True))
    op.add_column("brand_profile", sa.Column("project_id", sa.String(255), nullable=True))
    op.add_column("audience_profile", sa.Column("project_id", sa.String(255), nullable=True))
    op.add_column("test_rubric", sa.Column("project_id", sa.String(255), nullable=True))
    op.add_column("test_run", sa.Column("project_id", sa.String(255), nullable=True))
    op.add_column("report", sa.Column("project_id", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("report", "project_id")
    op.drop_column("test_run", "project_id")
    op.drop_column("test_rubric", "project_id")
    op.drop_column("audience_profile", "project_id")
    op.drop_column("brand_profile", "project_id")
    op.drop_column("creative_asset", "project_id")
    op.drop_table("export_job")
    op.drop_table("knowledge_item")
    op.drop_table("brandbook_document")
    op.drop_table("project")
    op.drop_table("client")
    op.drop_table("user")
