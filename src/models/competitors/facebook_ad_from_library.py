from datetime import date, datetime, timedelta

from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from src.database.base_class import Base

from loguru import logger

test_to_keywords: dict[str, list[str]] = {
    "promotion": ["save", "off", "discount", "code"],
    "addressing_the_user": ["you", "your", "?"],
    "call_to_action": ["shop", "browse", "visit", "learn", "sign", "call", "contact", "get", "click"],
    "price_mentioned": ["$", "USD"],
    "shipping_data": ["shipping", "deliver"],
    "urgency": ["limited", "today", "now"],
}

test_titles: dict[str, str] = {
    "promotion": "Promotion",
    "addressing_the_user": "Addressing the user",
    "call_to_action": "Call to action",
    "price_mentioned": "Price mentioned",
    "shipping_data": "Shipping data",
    "urgency": "Urgency",
}

test_titles_list: list[dict] = [
    {
        "test": key,
        "title": test_titles[key],
    }
    for key in test_titles.keys()
]


class FacebookAdFromLibrary(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        primary_key=True,
    )
    storage_date = Column(Date, primary_key=True)
    competitor_id = Column(BigInteger, ForeignKey("competitor.id"))
    ad_data = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    ad_screenshot_url = Column(String)
    checked = Column(Boolean)
    page_id = Column(BigInteger)

    @property
    def ad_type(self) -> str | None:
        if self.ad_data is None:
            return None
        try:
            display_format = str(self.ad_data["snapshot"]["display_format"])
            match display_format:
                case format if format in ["video", "carousel", "image"]:
                    return display_format
                case "multi_images":
                    return "image"
                case "multi_videos":
                    return "video"
                case "dpa":
                    return "dynamic_product"
                case "dco":
                    return "dynamic_creative"
                case _:
                    logger.warning(f"display_format: {display_format}")

        except Exception:
            logger.warning(f"Exception(ad_type) ad_id: {self.id}")

        try:
            snapshot_videos = self.ad_data["snapshot"]["videos"]
            if len(snapshot_videos) == 0:
                snapshot_videos = None
        except Exception:
            snapshot_videos = None

        if snapshot_videos is not None:
            return "video"
        else:
            return "other"

    @property
    def ad_text(self) -> str | None:
        if self.storage_date is None:
            return False
        try:
            return str(self.ad_data["snapshot"]["cards"][0]["body"])
        except Exception:
            try:
                return str(self.ad_data["snapshot"]["body"]["markup"]["__html"])
            except Exception:
                return None

    @property
    def ad_in_last_storage(self) -> bool:
        if self.storage_date is None:
            return False
        try:
            if self.storage_date < date.today() - timedelta(days=16):
                return False
            return True
        except Exception:
            logger.warning("ad_id = {self.id}")
            return False

    @property
    def start_date(self) -> date:
        try:
            return datetime.utcfromtimestamp(self.ad_data["startDate"]).date()
        except Exception:
            logger.warning(f"ad_id = {self.id}, startDate = {self.ad_data['startDate']}")
            return None

    @property
    def end_date(self) -> date | None:
        try:
            if self.ad_in_last_storage:
                if self.is_active:
                    return None
                else:
                    return datetime.utcfromtimestamp(self.ad_data["endDate"]).date()
            elif self.ad_data["endDate"] is None:
                return self.storage_date
            return datetime.utcfromtimestamp(self.ad_data["endDate"]).date()
        except Exception:
            logger.warning(f"ad_id = {self.id}, ad_in_last_storage = {self.ad_in_last_storage}")
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
    def account_is_logged_out(self) -> bool:
        try:
            if self.ad_data["gatedType"] == "logged_out":
                return True
            return False
        except Exception:
            logger.warning("cant read gatedType!")
            return False

    @property
    def invalid(self) -> bool:
        if self.start_date is None or self.account_is_logged_out:
            return True
        return False

    @property
    def ad_text_features(self) -> list[dict] | None:
        ad_text = self.ad_text
        if ad_text is None:
            return None

        words = ad_text.split(" ")
        features: list[dict] = []
        for test, keywords in test_to_keywords.items():
            for keyword in keywords:
                if keyword in words:
                    result = True
                    break
            else:
                result = False
            curent_test = {"test": test, "result": result}
            features.append(curent_test)
        return features
