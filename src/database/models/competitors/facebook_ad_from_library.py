from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database.base_class import Base

test_to_keywords: dict[str, list[str]] = {
    "promotion": ["save", "off", "discount", "code"],
    "addressing_the_user": ["you", "your", "?"],
    "call_to_action": ["shop", "browse", "visit", "learn", "sign", "call", "contact", "get", "click"],
    "price_mentioned": ["$", "USD"],
    "shipping_data": ["shipping", "deliver"],
    "urgency": ["limited", "today", "now"],
}


class FacebookAdFromLibrary(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        primary_key=True,
    )
    storage_date = Column(Date)
    competitor_id = Column(BigInteger, ForeignKey("competitor.id"))
    ad_data = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    ad_screenshot_url = Column(String)
    checked = Column(Boolean)

    competitor = relationship("Competitor", back_populates="facebook_ads")

    @property
    def ad_type(self) -> str | None:
        if self.ad_data is None:
            return None
        try:
            display_format = str(self.ad_data["snapshot"]["display_format"])
        except Exception:
            display_format = None
        try:
            video_preview_image_url = self.ad_data["snapshot"]["cards"][0]["video_preview_image_url"]
        except Exception:
            video_preview_image_url = None
        if display_format == "carousel":
            return "carousel"
        elif video_preview_image_url is not None and display_format == "video":
            return "video"
        else:
            return "image"

    @property
    def ad_text(self) -> str | None:
        if self.ad_data is None:
            return None
        try:
            return str(self.ad_data["snapshot"]["cards"][0]["body"])
        except Exception:
            try:
                return str(self.ad_data["snapshot"]["body"]["markup"]["__html"])
            except Exception:
                return None

    @property
    def start_date(self) -> date:
        return datetime.utcfromtimestamp(self.ad_data["startDate"]).date()

    @property
    def end_date(self) -> date | None:
        try:
            return datetime.utcfromtimestamp(self.ad_data["endDate"]).date()
        except Exception:
            return None

    @property
    def running_days(self) -> int | None:
        if self.ad_data is None:
            return None
        try:
            return int((self.ad_data["endDate"] - self.ad_data["startDate"]) / (60 * 60 * 24))
        except Exception:
            return None

    @property
    def is_active(self) -> bool:
        return bool(self.ad_data["isActive"])

    @property
    def invalid(self) -> bool:
        try:
            _ = self.start_date
            if not self.is_active:
                return self.end_date is None
            return False
        except Exception:
            return True

    @property
    def ad_text_features(self) -> dict[str, bool] | None:
        ad_text = self.ad_text
        if ad_text is None:
            return None

        words = ad_text.split(" ")
        features: dict[str, bool] = {}
        for test, keywords in test_to_keywords.items():
            for keyword in keywords:
                if keyword in words:
                    result = True
                    break
            else:
                result = False
            features[test] = result
        return features
