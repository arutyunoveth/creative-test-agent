"""Verify data survives a restart simulation (file-based SQLite, not :memory:).

Uses its own SQLAlchemy engine to avoid interfering with the test suite's global engine.
"""

import os
import tempfile

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.shared.db.base import Base


def _create_tables(engine):
    """Import all models and create tables on the given engine."""
    import src.modules.audit_log.models  # noqa: F401
    import src.modules.audience_profiles.models  # noqa: F401
    import src.modules.brand_profiles.models  # noqa: F401
    import src.modules.creative_assets.models  # noqa: F401
    import src.modules.report_generator.models  # noqa: F401
    import src.modules.test_rubrics.models  # noqa: F401
    import src.modules.test_runs.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def test_data_survives_restart():
    """Create data, close engine, re-init — data should still be there."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # --- Phase 1: create schema and data ---
        engine1 = create_engine(f"sqlite:///{db_path}", echo=False,
                                connect_args={"check_same_thread": False})
        _create_tables(engine1)
        Session1 = sessionmaker(bind=engine1)

        bp_id = None
        asset_id = None
        with Session1() as session:
            from src.modules.brand_profiles.models import BrandProfile
            from src.modules.creative_assets.models import CreativeAsset

            bp = BrandProfile(name="Restart Test Brand", tone_of_voice="Professional",
                              target_audience="Test", restrictions="None")
            session.add(bp)
            session.flush()
            bp_id = bp.id

            asset = CreativeAsset(title="Restart Asset", asset_type="text",
                                  text_content="Hello persistence")
            session.add(asset)
            session.flush()
            asset_id = asset.id
            session.commit()

        engine1.dispose()

        # --- Phase 2: simulate restart with a fresh engine on the same file ---
        engine2 = create_engine(f"sqlite:///{db_path}", echo=False,
                                connect_args={"check_same_thread": False})
        _create_tables(engine2)
        Session2 = sessionmaker(bind=engine2)

        with Session2() as session:
            from src.modules.brand_profiles.models import BrandProfile
            from src.modules.creative_assets.models import CreativeAsset

            bp = session.query(BrandProfile).filter(BrandProfile.id == bp_id).first()
            assert bp is not None, "Brand profile lost after restart"
            assert bp.name == "Restart Test Brand"

            asset = session.query(CreativeAsset).filter(CreativeAsset.id == asset_id).first()
            assert asset is not None, "Creative asset lost after restart"
            assert asset.title == "Restart Asset"

            count = session.query(CreativeAsset).count()
            assert count > 0, "No assets found after restart"

        engine2.dispose()

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
