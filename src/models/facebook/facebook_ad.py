from loguru import logger
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property


from src.database.base_class import Base
from src.models.enums import EPlatform


class FacebookAd(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    ad_id = Column(String, primary_key=True)
    adset_id = Column(String)
    campaign_id = Column(String)
    creative_id = Column(String)
    name = Column(String)
    status = Column(String)
    created_time = Column(DateTime(timezone=True))
    body_text = Column(String)
    ad_language = Column(String)
    creative = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    platform = EPlatform.facebook

    @hybrid_property
    def image_ad_image_hash(self) -> str | None:
        return self.creative.get("object_story_spec", {}).get("link_data", {}).get("image_hash")

    @image_ad_image_hash.expression
    def image_ad_image_hash(cls):
        logger.debug("expression")
        return cls.creative["object_story_spec"]["link_data"]["image_hash"]
