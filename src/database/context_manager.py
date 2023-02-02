from sqlalchemy.orm import Session

from src.database.session import SessionLocal


class DatabaseContextManager:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self) -> Session:
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()
