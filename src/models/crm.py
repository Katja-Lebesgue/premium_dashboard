from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, Date, TIMESTAMP

from src.database.base_class import Base


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
