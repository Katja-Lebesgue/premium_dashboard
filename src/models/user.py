from sqlalchemy import BigInteger, Boolean, Column, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src import models
from src.database.base_class import Base
from src.models.enums.appsumo.plan import plan_to_shop_number as appsumo_plan_to_shop_number


class User(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    shops = relationship("Shop", back_populates="owner")
    appsumo_license = relationship("AppsumoLicense", back_populates="user", uselist=False)
    appsumo_purchases = relationship("AppsumoPurchase", back_populates="user", lazy="dynamic")

    @property
    def max_shop_number(self) -> int:
        if self.appsumo_license:
            shop_number = appsumo_plan_to_shop_number[self.appsumo_license.plan]
        else:
            shop_number = 1
        return shop_number

    @property
    def purchase(self):
        return self.appsumo_purchases.order_by(models.AppsumoPurchase.created_at.desc()).first()

    def __str__(self):
        return f"{self.email} (id {self.id})"
