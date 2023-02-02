from datetime import datetime
from sqlalchemy import JSON, BigInteger, Column, String, DateTime
from src.database.base_class import Base


class CeleryFailedTask(Base):
    id = Column(BigInteger, primary_key=True)
    task_name = Column(String, nullable=False)
    exc = Column(String, nullable=False)
    task_id = Column(String, nullable=False)
    args = Column(JSON, nullable=False)
    kwargs = Column(JSON, nullable=False)
    einfo = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
