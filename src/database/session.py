from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings


engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_size=32, max_overflow=64)

print(str(engine))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
