from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Column, Date, Float, Integer, String, func, case
from sqlalchemy.ext.hybrid import hybrid_property

from src.database.base_class import Base
from src.models.enums import Industry


class Crm(Base):
    shop_id = Column(BigInteger, primary_key=True)
    install_yearmonth = Column(String(7), nullable=False)
    free_trial_ended = Column(String(3), nullable=False)
    google_connected = Column(Boolean)
    facebook_connected = Column(Boolean)
    tik_tok_connected = Column(Boolean)
    billing_plan = Column(String(255))
    amount = Column(String(15))
    started_paying = Column(TIMESTAMP(timezone=False))
    accepted_billing_date = Column(TIMESTAMP(timezone=False))
    accepted_billing_date_yearmonth = Column(String(7))
    is_paying = Column(String(3), nullable=False)
    was_paying = Column(String(3), nullable=False)
    orders_last_30days = Column(Integer)
    revenue_last_30days = Column(Float)
    relevant = Column(String(3), nullable=False)
    shop_size = Column(String, nullable=False)
    login_url = Column(String, nullable=False)
    uninstall_date = Column(Date)
    total_active_competitors = Column(Integer)
    industry = Column(String)
    acquisition_channel = Column(String)
    shopify_app_store_keyword = Column(String)
    reply_received = Column(String)
    notes = Column(String)
    is_paying_or_appsumo = Column(String(3), nullable=False)

    @hybrid_property
    def industry_enum(self) -> Industry:
        if not len(self.industry):
            return Industry.unknown
        return Industry(self.industry.lower().replace(" ", "_"))

    @industry_enum.expression
    def industry_enum(cls):
        return case(
            [(func.length(cls.industry) == 0, "unknown")],
            else_=func.lower(func.replace(cls.industry, " ", "_")),
        )
