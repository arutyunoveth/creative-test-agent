import json
from contextlib import contextmanager

from src.shared.db.session import create_session


@contextmanager
def db_session():
    db = create_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def json_dumps(val):
    return json.dumps(val, default=str) if val is not None else None


def json_loads(val):
    if val is None:
        return {}
    if val == "":
        return {}
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return {}
