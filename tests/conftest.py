import pytest
from sqlalchemy.pool import StaticPool

from src.shared.db.session import init_db, reset_engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    reset_engine(
        url="sqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    init_db()
    yield
