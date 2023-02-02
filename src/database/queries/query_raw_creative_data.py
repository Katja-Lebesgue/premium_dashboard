import sys

sys.path.append("././.")

import pandas as pd
from datetime import date
from sqlalchemy import func

from src.database.models.facebook.facebook_ad import FacebookAd
from src.database.models.facebook.facebook_adset import FacebookAdset
from src.database.models.credentials import Credentials
from src.database.session import SessionLocal
from src.database.myDB import DBConnect
from src.utils.help_functions import element_to_list, nan_to_none


def ping_creative_data_by_ad_id(ad_id: str | list[str]) -> pd.DataFrame:

    cursor = DBConnect()

    if type(ad_id) == str:
        ad_id = [ad_id]

    query = f"""
    select distinct facebook_ad.ad_id, facebook_ad.account_id, facebook_ad.shop_id, facebook_ad.creative_id, facebook_ad.creative,
            crd.access_token, facebook_adset.target, facebook_adset.targeting, facebook_ad.created_time,
            facebook_adset.targeting -> 'geo_locations' -> 'countries' as countries,
            facebook_ad.creative -> 'body' as body,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'message' as video_message,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'message' as link_message,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'message' as template_message,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'description' as template_description,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'title' as video_title,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'name' as link_name,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'name' as template_name,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'video_id' as video_id,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'image_url' as video_image_url,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'image_hash' as video_image_hash,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'link_description' as video_description,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'description' as link_description,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'child_attachments' as children,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'call_to_action' -> 'type' as link_cta,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'call_to_action' -> 'type' as video_cta,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'call_to_action' -> 'type' as template_cta,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'multi_share_end_card' as multi_share_end_card,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'show_multiple_images' as show_multiple_images,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'image_hash' as image_hash,
            facebook_ad.creative -> 'asset_feed_spec'-> 'bodies' as bodies,
            facebook_ad.creative -> 'asset_feed_spec'-> 'titles' as titles,
            facebook_ad.creative -> 'asset_feed_spec'-> 'descriptions' as descriptions,
            facebook_ad.creative -> 'asset_feed_spec'-> 'ad_formats' as ad_formats,
            facebook_ad.creative -> 'asset_feed_spec' -> 'images' as images,
            facebook_ad.creative -> 'asset_feed_spec' -> 'videos' as videos,

            facebook_ad.creative -> 'asset_feed_spec' -> 'call_to_action_types' as cta_types
        from facebook_ad
        left join (
            select cr.access_token, shop_id from (
                select access_token, shop_id,
                    ROW_NUMBER() OVER (PARTITION BY shop_id ORDER BY created_date_time DESC) AS rank
                from credentials
                where credentials_provider = 'FACEBOOK'
                and expired = false
                ) as cr
            where rank = 1
            ) as crd
        on facebook_ad.shop_id = crd.shop_id
        left join facebook_adset
        on facebook_ad.adset_id = facebook_adset.adset_id
        where facebook_ad.ad_id in %s
        """

    variables = (tuple(ad_id),)

    cursor.execute(query, variables)

    data = cursor.fetchall()
    cols = []

    for elt in cursor.description:
        cols.append(elt[0])

    df = pd.DataFrame(data=data, columns=cols)

    return df


def query_raw_creative_data(
    session=SessionLocal(),
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    add_texts: bool = True,
    add_images: bool = True,
    add_video_data: bool = True,
    add_link_data: bool = True,
    add_template_data: bool = True,
) -> pd.DataFrame:

    columns = [
        FacebookAd.ad_id,
        FacebookAd.account_id,
        FacebookAd.shop_id,
        FacebookAd.creative_id,
        FacebookAd.creative,
        FacebookAd.creative["asset_feed_spec"]["ad_formats"].label("ad_formats"),
        FacebookAd.creative["asset_feed_spec"]["cal_to_action_types"].label(
            "cta_types"
        ),
    ]

    if add_texts:
        columns.extend(
            [
                FacebookAd.creative["body"].label("body"),
                FacebookAd.creative["asset_feed_spec"]["bodies"].label("bodies"),
                FacebookAd.creative["asset_feed_spec"]["titles"].label("titles"),
                FacebookAd.creative["asset_feed_spec"]["descriptions"].label(
                    "descriptions"
                ),
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
                FacebookAd.creative["object_story_spec"]["video_data"]["message"].label(
                    "video_message"
                ),
                FacebookAd.creative["object_story_spec"]["video_data"][
                    "video_id"
                ].label("video_id"),
                FacebookAd.creative["object_story_spec"]["video_data"][
                    "image_url"
                ].label("video_image_url"),
                FacebookAd.creative["object_story_spec"]["video_data"][
                    "image_hash"
                ].label("video_image_hash"),
                FacebookAd.creative["object_story_spec"]["video_data"][
                    "link_description"
                ].label("video_description"),
                FacebookAd.creative["object_story_spec"]["video_data"]["title"].label(
                    "video_title"
                ),
                FacebookAd.creative["object_story_spec"]["video_data"][
                    "call_to_action"
                ]["type"].label("video_cta"),
                FacebookAd.creative["asset_feed_spec"]["videos"].label("videos"),
            ]
        )

    if add_link_data:
        columns.extend(
            [
                FacebookAd.creative["object_story_spec"]["link_data"]["message"].label(
                    "link_message"
                ),
                FacebookAd.creative["object_story_spec"]["link_data"]["name"].label(
                    "link_name"
                ),
                FacebookAd.creative["object_story_spec"]["link_data"][
                    "description"
                ].label("link_description"),
                FacebookAd.creative["object_story_spec"]["link_data"]["call_to_action"][
                    "type"
                ].label("link_cta"),
                FacebookAd.creative["object_story_spec"]["link_data"][
                    "child_attachments"
                ].label("children"),
                FacebookAd.creative["object_story_spec"]["link_data"][
                    "image_hash"
                ].label("image_hash"),
            ]
        )

    if add_template_data:
        columns.extend(
            [
                FacebookAd.creative["object_story_spec"]["template_data"][
                    "message"
                ].label("template_message"),
                FacebookAd.creative["object_story_spec"]["template_data"]["name"].label(
                    "template_name"
                ),
                FacebookAd.creative["object_story_spec"]["template_data"][
                    "description"
                ].label("template_description"),
                FacebookAd.creative["object_story_spec"]["template_data"][
                    "call_to_action"
                ]["type"].label("template_cta"),
                FacebookAd.creative["object_story_spec"]["template_data"][
                    "multi_share_end_card"
                ].label("multi_share_end_card"),
                FacebookAd.creative["object_story_spec"]["template_data"][
                    "show_multiple_images"
                ].label("show_multiple_images"),
            ]
        )

    query = session.query(*columns)

    if ad_id is not None:
        ad_id = element_to_list(ad_id)
        query = query.filter(FacebookAd.ad_id.in_(ad_id))

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        query = query.filter(FacebookAd.shop_id.in_(shop_id))

    query = query.distinct()

    return query


def main():
    session = SessionLocal()
    query = query_raw_creative_data(session=session, shop_id="2")
    df2 = pd.read_sql(query.statement, session.bind)
    print(df2)


if __name__ == "__main__":
    main()
