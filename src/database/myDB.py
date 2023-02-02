import sys
sys.path.append('./.')

import pandas as pd
import json
import numpy as np
import psycopg2
from datetime import date, datetime
import os
from dotenv import load_dotenv

load_dotenv()


def DBConnect() -> psycopg2.extensions.cursor:

    conn = psycopg2.connect(
        host=os.getenv("HOST"),
        database=os.getenv("DATABASE"),
        user=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
    )
    return conn.cursor()


def get_credentials(
    cursor: psycopg2.extensions.cursor, start_date: str, end_date: str = date.today().strftime("%Y-%m-%d")
) -> pd.DataFrame:
    """Function returns dataframe with valid Facebook credentials for ads created between start_date and end_date.

    Args:
        cursor (psycopg2.extensions.cursor): for db connection
        start_date (str):
        end_date (str, optional): Defaults to date.today().strftime('%Y/%m/%d').

    Returns:
        pd.DataFrame: contains columns credentials, shop_id, creative_id and creative
    """

    query = f"""
    select facebook_ad.ad_id, facebook_ad.account_id, facebook_ad.shop_id, facebook_ad.creative_id, facebook_ad.creative,
           crd.access_token, daily.date_start
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
    left join facebook_daily_performance as daily
    on daily.ad_id = facebook_ad.ad_id
    where date_start between %s and %s
    """

    variables = [start_date, end_date]
    cursor.execute(query, variables)
    data = cursor.fetchall()
    cols = []

    for elt in cursor.description:
        cols.append(elt[0])

    df = pd.DataFrame(data=data, columns=cols)

    return df


def get_creative_unpacked(
    cursor: psycopg2.extensions.cursor, start_date: str, end_date: str = date.today().strftime("%Y/%m/%d")
) -> pd.DataFrame:
    """Function returns dataframe with unpacked creative jsons.

    Args:
        cursor (psycopg2.extensions.cursor): for db connection
        start_date (str):
        end_date (str, optional): Defaults to date.today().strftime('%Y/%m/%d').

    Returns:
        pd.DataFrame:
    """

    query = f"""
    select facebook_ad.creative_id,
            facebook_ad.creative,

            facebook_ad.creative -> 'body' as body_standard,
            facebook_ad.creative -> 'asset_feed_spec' -> 'bodies' as body_multiple,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' ->> 'message' as body_image,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' ->> 'message' as body_video,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' ->> 'message' as body_catalog,

            facebook_ad.creative -> 'call_to_action_type' as cta_standard,
            facebook_ad.creative -> 'asset_feed_spec' -> 'call_to_action_types' as cta_multiple,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'call_to_action' -> 'type' as cta_image,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'call_to_action' -> 'type' as cta_video,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'call_to_action' -> 'type' as cta_catalog,

            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'title' as headline_image,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'name' as headline_image2,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'title' as headline_video,
            facebook_ad.creative -> 'asset_feed_spec' -> 'titles' as headline_multiple,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'name' as headline_catalog,

            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'link_description' as description_image,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'description' as description_image2,
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'link_description' as description_video,
            facebook_ad.creative -> 'asset_feed_spec' -> 'descriptions' as description_multiple,
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'description' as description_catalog,

            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'child_attachments' as child_data,

            facebook_ad.creative -> 'object_story_spec' -> 'video_data' ->> 'video_id' as video_id,
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' ->> 'image_hash' as image_hash_standard,
            facebook_ad.creative -> 'asset_feed_spec' -> 'images' as image_hash_multiple,

        facebook_daily_performance.ad_id,
        facebook_ad.status as ad_status,
        facebook_daily_performance.adset_id,
            facebook_adset.name as adset_name,
            facebook_adset.targeting,

            facebook_adset.targeting -> 'facebook_positions' as facebook_positions,
            facebook_adset.targeting -> 'instagram_positions' as instagram_positions,
            facebook_adset.targeting -> 'messenger_positions' as messenger_positions,
            facebook_adset.targeting -> 'publisher_platforms' as publisher_platforms,

            facebook_adset.target,

        sum(spend) as spend,
        sum(impressions) as impr,
        sum(clicks) as clicks,
        sum(purchases) as purch
    from facebook_daily_performance
    left join facebook_ad
    on facebook_daily_performance.ad_id = facebook_ad.ad_id
    left join facebook_adset
    on facebook_daily_performance.adset_id = facebook_adset.adset_id
    where date_start >= %s
    and date_start <= %s
    group by facebook_ad.creative_id,
            facebook_ad.creative,

            facebook_ad.creative -> 'body',
            facebook_ad.creative -> 'asset_feed_spec' -> 'bodies',
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' ->> 'message',
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' ->> 'message',
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' ->> 'message',

            facebook_ad.creative -> 'call_to_action_type',
            facebook_ad.creative -> 'asset_feed_spec' -> 'call_to_action_types',
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'call_to_action' -> 'type',
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'call_to_action' -> 'type',
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'call_to_ation' -> 'type',

            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'title',
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'name',
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'title',
            facebook_ad.creative -> 'asset_feed_spec' -> 'titles',
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'name',

            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'link_description',
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'description',
            facebook_ad.creative -> 'object_story_spec' -> 'video_data' -> 'link_description',
            facebook_ad.creative -> 'asset_feed_spec' -> 'descriptions',
            facebook_ad.creative -> 'object_story_spec' -> 'template_data' -> 'description',

            facebook_ad.creative -> 'object_story_spec' -> 'link_data' -> 'child_attachments',

            facebook_ad.creative -> 'object_story_spec' -> 'video_data' ->> 'video_id',
            facebook_ad.creative -> 'object_story_spec' -> 'link_data' ->> 'image_hash',
            facebook_ad.creative -> 'asset_feed_spec' -> 'images',

        facebook_daily_performance.ad_id,
        facebook_ad.status,
        facebook_daily_performance.adset_id,
            facebook_adset.name,
            facebook_adset.targeting,

            facebook_adset.targeting -> 'facebook_positions',
            facebook_adset.targeting -> 'instagram_positions',
            facebook_adset.targeting -> 'messenger_positions',
            facebook_adset.targeting -> 'publisher_platforms',

            facebook_adset.target
    order by sum(spend)
    """

    variables = [start_date, end_date]
