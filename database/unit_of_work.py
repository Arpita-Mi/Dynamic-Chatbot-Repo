from contextlib import contextmanager
from fastapi import HTTPException



@contextmanager
def SqlAlchemyUnitOfWork(session):
    db = session()
    try:
        yield db
    except Exception as e:
        error_msg = str(e.detail) if isinstance(e, HTTPException) else str(e)
        db.rollback()
        raise HTTPException(400, error_msg)
    finally:
        db.close()
