from datetime import date

import pandas as pd
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from src.crud.base import CRUDBase
from src.models.facebook.facebook_ad import FacebookAd
from src.models.facebook.facebook_daily_performance import \
    FacebookDailyPerformance
from src.schemas.facebook.facebook_ad import FacebookAdCreate, FacebookAdUpdate
from src.utils import element_to_list


class CRUDFacebookAd(CRUDBase[FacebookAd, FacebookAdCreate, FacebookAdUpdate]):
    def get(self, db: Session, shop_id: int, account_id: str, ad_id: str) -> FacebookAd | None:
        return db.query(self.model).get((shop_id, account_id, ad_id))

    def get_names(self, db: Session, shop_id: int, ad_id: str | list[str] | None = None) -> list[FacebookAd]:
        query = db.query(self.model.ad_id, self.model.account_id, self.model.name)
        filters = [self.model.shop_id == shop_id]
        if ad_id is not None:
            ad_id = element_to_list(ad_id)
            filters.append(self.model.account_id.in_(ad_id))

        return query.filter(*filters).all()

    def query_raw_creative_data(
        self,
        db: Session,
        ad_id: str | list[str] | None = None,
        shop_id: int | list[int] | None = None,
        account_id: str | list[str] | None = None,
        add_texts: bool = True,
        add_images: bool = True,
        add_video_data: bool = True,
        add_link_data: bool = True,
        add_template_data: bool = True,
    ) -> Query:
        """Creates query for pinging creative data extracted from jsons in FacebookAd table.

        Args:
            db (Session):
            ad_id (str | list[str] | None, optional): filtered ad ids.
                If None, query is not filtered by ad id. Defaults to None.
            shop_id (int | list[int] | None, optional): filtered shop ids.
                If None, query is not filtered by shop id. Defaults to None.
            account_id (str | list[str] | None, optional): filtered account ids.
                If None, query is not filtered by account id. Defaults to None.
            add_texts (bool, optional): Defaults to True.
            add_images (bool, optional): Defaults to True.
            add_video_data (bool, optional): Defaults to True.
            add_link_data (bool, optional): Defaults to True.
            add_template_data (bool, optional): Defaults to True.

        Returns:
            Query: generated query
        """

        columns = [
            FacebookAd.ad_id,
            FacebookAd.account_id,
            FacebookAd.shop_id,
            FacebookAd.creative_id,
            FacebookAd.creative,
            FacebookAd.creative["asset_feed_spec"]["ad_formats"].label("ad_formats"),
            FacebookAd.creative["asset_feed_spec"]["call_to_action_types"].label("cta_types"),
        ]

        if add_texts:
            columns.extend(
                [
                    FacebookAd.creative["body"].label("body"),
                    FacebookAd.creative["asset_feed_spec"]["bodies"].label("bodies"),
                    FacebookAd.creative["asset_feed_spec"]["titles"].label("titles"),
                    FacebookAd.creative["asset_feed_spec"]["descriptions"].label("descriptions"),
                ]
            )

        if add_images:
            columns.extend(
                [
                    FacebookAd.creative["asset_feed_spec"]["images"].label("images"),
                ]
            )

        if add_video_data:
            columns.extend(
                [
                    FacebookAd.creative["object_story_spec"]["video_data"]["message"].label("video_message"),
                    FacebookAd.creative["object_story_spec"]["video_data"]["video_id"].label("video_id"),
                    FacebookAd.creative["object_story_spec"]["video_data"]["image_url"].label(
                        "video_image_url"
                    ),
                    FacebookAd.creative["object_story_spec"]["video_data"]["image_hash"].label(
                        "video_image_hash"
                    ),
                    FacebookAd.creative["object_story_spec"]["video_data"]["link_description"].label(
                        "video_description"
                    ),
                    FacebookAd.creative["object_story_spec"]["video_data"]["title"].label("video_title"),
                    FacebookAd.creative["object_story_spec"]["video_data"]["call_to_action"]["type"].label(
                        "video_cta"
                    ),
                    FacebookAd.creative["asset_feed_spec"]["videos"].label("videos"),
                ]
            )

        if add_link_data:
            columns.extend(
                [
                    FacebookAd.creative["object_story_spec"]["link_data"]["message"].label("link_message"),
                    FacebookAd.creative["object_story_spec"]["link_data"]["name"].label("link_name"),
                    FacebookAd.creative["object_story_spec"]["link_data"]["description"].label(
                        "link_description"
                    ),
                    FacebookAd.creative["object_story_spec"]["link_data"]["call_to_action"]["type"].label(
                        "link_cta"
                    ),
                    FacebookAd.creative["object_story_spec"]["link_data"]["child_attachments"].label(
                        "children"
                    ),
                    FacebookAd.creative["object_story_spec"]["link_data"]["image_hash"].label("image_hash"),
                ]
            )

        if add_template_data:
            columns.extend(
                [
                    FacebookAd.creative["object_story_spec"]["template_data"]["message"].label(
                        "template_message"
                    ),
                    FacebookAd.creative["object_story_spec"]["template_data"]["name"].label("template_name"),
                    FacebookAd.creative["object_story_spec"]["template_data"]["description"].label(
                        "template_description"
                    ),
                    FacebookAd.creative["object_story_spec"]["template_data"]["call_to_action"]["type"].label(
                        "template_cta"
                    ),
                    FacebookAd.creative["object_story_spec"]["template_data"]["multi_share_end_card"].label(
                        "multi_share_end_card"
                    ),
                    FacebookAd.creative["object_story_spec"]["template_data"]["show_multiple_images"].label(
                        "show_multiple_images"
                    ),
                ]
            )

        query = db.query(*columns)

        if ad_id is not None:
            ad_id = element_to_list(ad_id)
            query = query.filter(FacebookAd.ad_id.in_(ad_id))

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            query = query.filter(FacebookAd.shop_id.in_(shop_id))

        if account_id is not None:
            account_id = element_to_list(account_id)
            query = query.filter(FacebookAd.account_id.in_(account_id))

        query = query.distinct()

        return query


fb_ad = CRUDFacebookAd(FacebookAd)
