from sqlalchemy import (TIMESTAMP, BigInteger, Boolean, Column, Enum,
                        ForeignKey, Integer, String, func)
from sqlalchemy.dialects import postgresql, sqlite

from src.database.base_class import Base
from src.models.enums.facebook.adset import Target
from src.models.enums.facebook.creative_features import CreativeType


class FacebookCreativeFeatures(Base):
    # primary key
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    ad_id = Column(String, primary_key=True)

    creative_id = Column(String)
    creative_type = Column(Enum(CreativeType, native_enum=False))

    # texts
    title = Column(postgresql.ARRAY(String).with_variant(sqlite.JSON, "sqlite"), server_default="{}")
    primary = Column(postgresql.ARRAY(String).with_variant(sqlite.JSON, "sqlite"), server_default="{}")
    description = Column(postgresql.ARRAY(String).with_variant(sqlite.JSON, "sqlite"), server_default="{}")

    # text features
    cta = Column(Boolean)
    discount = Column(Boolean)
    emoji = Column(Boolean)
    emoji_list = Column(postgresql.ARRAY(String).with_variant(sqlite.JSON, "sqlite"), server_default="{}")
    free_shipping = Column(Boolean)
    fact_words = Column(Boolean)
    hashtag = Column(Boolean)
    link = Column(Boolean)
    percentage = Column(Boolean)
    price = Column(Boolean)
    starts_with_question = Column(Boolean)
    urgency = Column(Boolean)
    user_addressing = Column(Boolean)
    weasel_words = Column(Boolean)

    # target features
    age_range = Column(Integer)
    number_of_custom_audiences = Column(Integer)
    number_of_countries = Column(Integer)
    target = Column(Enum(Target, native_enum=False))
    targets_english = Column(Boolean)
    targets_US = Column(Boolean)

    # update metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )
