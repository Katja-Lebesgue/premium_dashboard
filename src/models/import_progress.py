from sqlalchemy import BigInteger, Column, Enum, ForeignKey, Integer, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.enums.common.data_source import DataSource
from src.enums.common.import_type import ImportType


class ImportProgress(Base):
    id = Column(BigInteger, primary_key=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    source = Column(Enum(DataSource, native_enum=False), nullable=False)
    account_id = Column(BigInteger, nullable=True)
    type = Column(Enum(ImportType, native_enum=False), nullable=True)
    num_total_tasks = Column(Integer, nullable=False)
    num_completed_tasks = Column("num_completed_tasks", Integer, nullable=False, default=0)
    num_failed_tasks = Column("num_failed_tasks", Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    shop = relationship("Shop")

    @property
    def is_full_import(self) -> bool:
        return self.type == ImportType.full

    @property
    def is_finished(self) -> bool:
        return self.num_total_tasks == (self.num_completed_tasks + self.num_failed_tasks)
