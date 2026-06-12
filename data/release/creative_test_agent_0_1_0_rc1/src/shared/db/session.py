import re

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.shared.config.settings import get_settings

_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, echo=settings.debug, connect_args={"check_same_thread": False})
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _session_factory


def create_session() -> Session:
    return get_session_factory()()


def init_db():
    from src.shared.db.base import Base
    import src.modules.audit_log.models  # noqa: F401
    import src.modules.audience_profiles.models  # noqa: F401
    import src.modules.brand_profiles.models  # noqa: F401
    import src.modules.creative_assets.models  # noqa: F401
    import src.modules.report_generator.models  # noqa: F401
    import src.modules.test_rubrics.models  # noqa: F401
    import src.modules.test_runs.models  # noqa: F401
    import src.modules.users.models  # noqa: F401
    import src.modules.clients.models  # noqa: F401
    import src.modules.projects.models  # noqa: F401
    import src.modules.brandbooks.models  # noqa: F401
    import src.modules.knowledge_base.models  # noqa: F401
    import src.modules.export_jobs.models  # noqa: F401
    import src.modules.model_profiles.models  # noqa: F401
    import src.modules.prompt_registry.models  # noqa: F401
    import src.modules.evaluations.models  # noqa: F401
    import src.modules.prompt_traces.models  # noqa: F401
    import src.modules.reviews.models  # noqa: F401
    import src.modules.job_queue.models  # noqa: F401
    import src.modules.batches.models  # noqa: F401
    Base.metadata.create_all(bind=get_engine())


def close_db():
    global _engine, _session_factory
    if _engine:
        _engine.dispose()
    _engine = None
    _session_factory = None


def reset_engine(url: str | None = None, echo: bool = False, poolclass=None, connect_args=None):
    global _engine, _session_factory
    close_db()
    if url:
        kwargs = {"echo": echo}
        if poolclass:
            kwargs["poolclass"] = poolclass
        if connect_args:
            kwargs["connect_args"] = connect_args
        _engine = create_engine(url, **kwargs)


def check_db_connection() -> bool:
    """Execute a lightweight query to verify the database is reachable."""
    try:
        with create_session() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def mask_database_url(url: str) -> str:
    """Mask the password portion of a database URL, if present."""
    masked = re.sub(r":([^:@/]+)@", r":****@", url)
    return masked


def get_database_url(masked: bool = True) -> str:
    url = get_settings().database_url
    if masked:
        return mask_database_url(url)
    return url
