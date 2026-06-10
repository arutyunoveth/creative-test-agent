from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.shared.config.settings import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
