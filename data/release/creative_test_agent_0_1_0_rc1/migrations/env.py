from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from src.shared.config.settings import get_settings
from src.shared.db.base import Base

# Ensure all models are registered with Base.metadata
import src.modules.audit_log.models  # noqa: F401
import src.modules.audience_profiles.models  # noqa: F401
import src.modules.brand_profiles.models  # noqa: F401
import src.modules.creative_assets.models  # noqa: F401
import src.modules.report_generator.models  # noqa: F401
import src.modules.test_rubrics.models  # noqa: F401
import src.modules.test_runs.models  # noqa: F401
import src.modules.model_profiles.models  # noqa: F401
import src.modules.prompt_registry.models  # noqa: F401
import src.modules.evaluations.models  # noqa: F401
import src.modules.prompt_traces.models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    """Return the database URL, preferring a programmatic override over
    alembic.ini, falling back to application settings."""
    ini_url = config.get_main_option("sqlalchemy.url")
    default_url = "sqlite:///./creative_test_agent.db"
    # If the config URL was explicitly overridden (e.g. via set_main_option
    # in tests), use it.
    if ini_url and ini_url != default_url:
        return ini_url
    # Fall back to application settings so the URL stays in sync with
    # CTA_DATABASE_URL at runtime.
    try:
        settings = get_settings()
        app_url = settings.database_url
        return app_url
    except Exception:
        return default_url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
