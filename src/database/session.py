from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

import os
from dotenv import load_dotenv

load_dotenv()

uri = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_SERVER")}/{os.getenv("POSTGRES_DB")}'

engine = create_engine(uri, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

logger.debug(f'base: {os.getenv("POSTGRES_SERVER")}')
